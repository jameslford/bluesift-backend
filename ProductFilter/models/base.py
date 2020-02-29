import uuid
from typing import List
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from django.http import QueryDict
from django.contrib.postgres import fields as pg_fields
from Suppliers.models import SupplierLocation
from ..tasks import add_facet_others_delay, add_query_index



class BaseReturnValue:
    def __init__(self, expression: str, name: str, count: int = None, value=None, color=False):
        self.expression = expression
        self.name = name
        self.count = count
        self.value = value
        self.color = color

    def asdict(self):
        return {
            'name': self.name,
            'count': self.count,
            'color': self.color,
            'expression': self.expression,
            'selected': self.value
            }


class BaseFacet(models.Model):
    limit = models.Q(app_label='Products') | models.Q(app_label='SpecializedProducts')
    name = models.CharField(max_length=20, blank=True)
    widget = models.CharField(max_length=30, default='checkbox')
    dynamic = models.BooleanField(default=False)
    editable = models.BooleanField(default=False)
    field_type = models.CharField(max_length=70, default='CharField')
    proxy_type = models.CharField(max_length=60, default='CharFacet')
    abs_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    abs_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    allow_multiple = models.BooleanField(default=True)

    attribute = models.CharField(max_length=60, null=True, blank=True)
    attribute_list = pg_fields.ArrayField(
        models.CharField(max_length=60, null=True, blank=True),
        null=True,
        blank=True
        )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit
        )
    static_charfield_values = pg_fields.ArrayField(
        models.CharField(max_length=80, null=True, blank=True),
        null=True,
        blank=True
        )

    objects = models.Manager()


    class Meta:
        unique_together = ('attribute', 'content_type', 'attribute_list')


    def __str__(self):
        return f'{self.model.__name__}, {self.name}'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.qterms = []
        self.selected = False
        self.selected_min = None
        self.selected_max = None
        self.radius = None
        self.zipcode = None
        self.return_values: List[BaseReturnValue] = []
        self.enabled_values: List[BaseReturnValue] = []
        self.queryset: QuerySet = None
        self.others_intersection: QuerySet = None
        self.model = self.content_type.model_class()
        self.exclusive = False



    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.attribute and self.attribute_list:
            raise Exception('cannot have attribute and attribute list')
        if self.attribute:
            if self.attribute == 'low_price':
                return super().save(
                    force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
            field = self.model._meta.get_field(self.attribute)
            actual_type = field.get_internal_type()
            if self.field_type != actual_type:
                raise Exception(f'Attribute -{self.attribute}\'s- field type {actual_type} != {self.field_type}')
        if not self.name:
            self.name = self.attribute
        if not self.proxy_type:
            self.proxy_type = self.__class__.__name__
        return super().save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


    def parse_request(self, params: QueryDict):
        qterms = params.getlist(self.name, None)
        qterms = qterms[0].split(',') if qterms else []
        if self.attribute:
            values = self.get_charfield_values()
        else:
            values = self.attribute_list
        self.qterms = [term for term in qterms if str(term) in values]
        return params

    def get_charfield_values(self):
        if self.static_charfield_values:
            return self.static_charfield_values
        values = list(self.model.objects.values_list(self.attribute, flat=True).distinct())
        if self.dynamic:
            return values
        self.static_charfield_values = values
        self.save()
        return values


    def get_search_values(self):
        '''use by SearchIndex model to get values '''
        if self.field_type != 'CharField':
            return None
        if self.attribute:
            values = self.model.values(self.attribute)
            return [{'tag': value, 'express': f'{self.attribute}={value}'} for value in values]


    def return_stock(self):
        self.queryset = self.model.objects.values_list('pk', flat=True)
        return self.queryset


    def filter_self(self):
        raise Exception(f'{self.field_type} must be subclassed')


    def __calc_intersections(self, products, others):
        new_prods = products
        for qset in others:
            if qset:
                new_prods = new_prods.filter(pk__in=qset)
        return products


    def get_intersection(self, query_index_pk, products, others: List[QuerySet]):
        if self.dynamic:
            return self.__calc_intersections(products, others)
        cached_others: FacetOthersCollection = FacetOthersCollection.objects.filter(query_index__pk=query_index_pk, facet=self).first()
        if cached_others:
            return cached_others.products
        others = [oth for oth in others if oth]
        result = products.intersection(*others)
        values = list(result.values_list('pk', flat=True))
        add_facet_others_delay.delay(query_index_pk, self.pk, values)
        return self.model.objects.filter(pk__in=values)

    # pylint: disable=unused-argument
    def count_self(self, query_index_pk, facets, products=None):
        return None


    def serialize_self(self):
        return_dict = {
            'name': self.name,
            'selected': self.selected,
            'widget': self.widget,
            'editable': True,
            'exclusive': self.exclusive,
            'all_values': [value.asdict() for value in self.return_values],
            }
        return return_dict





class QueryIndexManager(models.Manager):
    def get_or_create_qi(self, **kwargs):
        query_dict = kwargs.get('query_dict')
        query_path = kwargs.get('query_path')
        # product_filter = kwargs.get('product_filter')
        retailer_location = kwargs.get('retailer_location')
        args = {
            'query_dict': query_dict,
            'query_path': query_path,
            # 'product_filter': product_filter
            }
        if retailer_location:
            location = SupplierLocation.objects.get(pk=retailer_location)
            args['retailer_location'] = location
        query_index = self.model.objects.get_or_create(**args)
        return query_index


class QueryIndex(models.Model):
    """
    cache relating query strings to json responses
    """
    query_dict = models.CharField(max_length=1000)
    query_path = models.CharField(max_length=500)
    dirty = models.BooleanField(default=True)
    retailer_location = models.ForeignKey(
        SupplierLocation,
        null=True,
        on_delete=models.CASCADE,
        related_name='qis'
        )
    products = models.ManyToManyField(
        'Products.Product',
        related_name='query_indexes'
        )
    created = models.DateTimeField(auto_now=True)
    last_retrieved = models.DateTimeField(auto_now_add=True, null=True)
    times_accessed = models.PositiveIntegerField(null=True, default=1)

    objects = QueryIndexManager()

    class Meta:
        unique_together = ('query_dict', 'query_path', 'retailer_location')

    def __str__(self):
        return f'{self.query_path}_{self.query_dict}'

    def add_products(self, products):
        # print(products)
        # products = products.values_list('pk', flat=True)
        add_query_index.delay(self.pk, products)


    def get_product_pks(self):
        return self.products.values_list('pk', flat=True)


class FacetOthersCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    query_index = models.ForeignKey(
        QueryIndex,
        on_delete=models.CASCADE,
        related_name='others'
        )
    facet = models.ForeignKey(
        BaseFacet,
        on_delete=models.CASCADE,
        null=True
    )
    products = models.ManyToManyField(
        'Products.Product',
        related_name='facet_collections'
    )

    class Meta:
        unique_together = ('query_index', 'facet')

    def __str__(self):
        return f'{self.facet.name} {str(self.query_index)}'

    def assign_new_products(self, products):
        self.products.clear()
        self.products.add(*products)
        self.save()

    def get_product_pks(self):
        return self.products.values_list('pk', flat=True)




        # if self.field_type == 'MultiPointField':
        #     return None
        # if self.field_type in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:

        #         return None
        #     return None
        # if self.field_type == 'BooleanField':
        #     return self.__count_bools(query_index_pk, products, facets)
        # if self.field_type == 'ForeignKey':
        #     return self.__count_foreignkey(query_index_pk, products, facets)
        # return self.__count_inclusive(query_index_pk, products, facets)

        # if self.field_type in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:
        #     qs = self.__filter_numeric()
        #     # print(qs.first())
        #     return qs

        # if self.field_type == 'CharField':
        #     qs = self.__filter_charfield()
        #     # print(qs.first())
        #     return qs

        # if self.field_type == 'ForeignKey':
        #     qs = self.__filter_foreignkey()
        #     # print(qs.first())
        #     return qs

        # if self.field_type == 'BooleanField':
        #     qs = self.__filter_boolean()
        #     # print(qs.first())
        #     return qs

        # if self.field_type == 'MultiPointField':
        #     qs = self.__filter_radius()
        #     # print(qs.first())
        #     return qs




        # print(self.field_type, self.name)
        # if self.field_type in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:
        #     return self.__parse_numeric(params)

        # if self.field_type in ['MultiPointField']:
        #     return self.__parse_radius(params)
            # values = list(self.model.objects.values_list(self.attribute, flat=True).distinct())

        # print(self.attribute)
        # print(self.qterms)
