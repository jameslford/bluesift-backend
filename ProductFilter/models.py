import uuid
from decimal import Decimal
from typing import List
from model_utils.managers import InheritanceManager
from django.db import models
from django.db.models import Min, Max
from django.db.models.query import QuerySet
from django.http import QueryDict
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields
from django.contrib.gis.measure import D
from Addresses.models import Zipcode
from Suppliers.models import SupplierLocation
from Products.models import Product
from .tasks import add_facet_others_delay



class BaseReturnValue:
    def __init__(self, expression: str, name: str, count: int = None, value=None):
        self.expression = expression
        self.name = name
        self.count = count
        self.value = value

    def asdict(self):
        return {
            'name': self.name,
            'count': self.count,
            'expression': self.expression,
            'selected': self.value
            }


class AvailabilityFacet:

    def __init__(self, location_pk):
        self.name = 'availability'
        self.qterms = []
        self.location_pk = location_pk
        self.queryset: QuerySet = None
        self.selected = False
        self.dynamic = True
        self.values = Product.objects.safe_availability_commands()
        self.return_values = []

    def parse_request(self, params: QueryDict):
        qterms = params.getlist(self.name)
        qterms = [term for term in qterms if term in self.values]
        for term in qterms:
            nterm = params.pop(term)
            self.qterms.append(nterm)
        return params

    def filter_self(self):
        products = Product.objects.all()
        if not self.qterms:
            self.queryset = products.values_list('pk', flat=True)
            return products
        self.selected = True
        products = products.filter_availability(self.qterms, self.location_pk, True)
        self.queryset = products.values_list('pk', flat=True)
        return products

    def count_self(self, query_index_pk, products, facets):
        _facets = [facet.queryset for facet in facets if facet is not self]
        others = products.intersection(*_facets).values_list('pk', flat=True)
        enabled_values = []
        for value in self.values:
            count = products.filter(pk__in=others).filter_availability(value, self.location_pk).count()
            selected = bool(value in self.qterms)
            expression = f'{self.name}={value}'
            return_value = BaseReturnValue(expression, self.name, count, selected)
            self.return_values.append(BaseReturnValue(expression, value, count, selected))
            if selected:
                enabled_values.append(return_value.asdict())
        return enabled_values

    def serialize_self(self):
        return {
            'name': self.name,
            'selected': self.selected,
            'widget': 'checkbox',
            'editabled': False,
            'all_values': [value.asdict() for value in self.return_values],
            # 'enabled_values': [value.asdict() for value in self.enabled_values]
            }


class BaseFacet(models.Model):
    limit = models.Q(app_label='Products') | models.Q(app_label='SpecializedProducts')
    name = models.CharField(max_length=20, blank=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit
        )
    attribute = models.CharField(max_length=60, null=True, blank=True)
    attribute_list = pg_fields.ArrayField(
        models.CharField(max_length=60, null=True, blank=True),
        null=True,
        blank=True
        )
    widget = models.CharField(max_length=30, default='checkbox')
    dynamic = models.BooleanField(default=False)
    editable = models.BooleanField(default=False)
    field_type = models.CharField(max_length=70, default='CharField')
    abs_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    abs_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    allow_multiple = models.BooleanField(default=True)
    # group_object = models.BooleanField(default=False)
    # values = pg_fields.JSONField(null=True, blank=True)

    qterms = None
    queryset = None
    selected = False
    selected_min = None
    selected_max = None
    radius = None
    zipcode = None
    enabled_values = None
    return_values = None
    queryset: QuerySet = None
    others_intersection: QuerySet = None


    objects = models.Manager()
    subclasses = InheritanceManager()


    class Meta:
        unique_together = ('attribute', 'content_type', 'attribute_list')


    def __str__(self):
        return f'{self.model.__name__}, {self.name}'


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
        else:
            for attr in self.attribute_list:
                field = self.model._meta.get_field(attr)
                actual_type = field.get_internal_type()
                if self.field_type != field.get_internal_type():
                    raise Exception(f'Attribute -{attr}\'s- field type {actual_type} != {self.field_type}')
        if not self.name:
            self.name = self.attribute
        return super().save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


    @property
    def model(self) -> models.Model:
        return self.content_type.model_class()


    def __get_absolutes(self):
        if self.field_type in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:
            if self.abs_min and self.abs_max:
                return [self.abs_max, self.abs_min]
            if self.attribute == 'low_price':
                absolutes = Product.objects.product_prices().aggregate(Min(self.attribute), Max(self.attribute))
            elif self.others_intersection:
                absolutes = self.others_intersection.aggregate(Min(self.attribute), Max(self.attribute))
            else:
                absolutes = self.model.objects.aggregate(Min(self.attribute), Max(self.attribute))
            abs_min = absolutes.get(f'{self.attribute}__min')
            abs_max = absolutes.get(f'{self.attribute}__max')
            if not self.dynamic:
                self.abs_min = abs_min
                self.abs_max = abs_max
                self.save()
            return [abs_max, abs_min]
        return None


    def __return_stock(self):
        self.queryset = self.model.objects.values_list('pk', flat=True)
        return Product.objects.filter(pk__in=self.queryset)


    def __filter_boolean(self):
        if not self.qterms:
            return self.__return_stock()
        if self.allow_multiple:
            term = {self.qterms[-1] : True}
            self.queryset = self.model.objects.filter(**term).values_list('pk', flat=True)
            return Product.objects.filter(pk__in=self.queryset)
        terms = {}
        for term in self.qterms:
            terms[term] = True
            self.selected = True
        self.queryset = self.model.objects.filter(**terms).values_list('pk', flat=True)
        return Product.objects.filter(pk__in=self.queryset)


    def __filter_charfield(self):
        if not self.qterms:
            return self.__return_stock()
        q_object = models.Q()
        for term in self.qterms:
            q_object |= models.Q(**{self.attribute: term})
            self.selected = True
        self.queryset = self.model.objects.filter(q_object).values_list('pk', flat=True)
        return Product.objects.filter(pk__in=self.queryset)


    def __filter_radius(self):
        if not (self.radius and self.zipcode):
            return self.__return_stock()
        try:
            radius = D(mi=int(self.radius))
        except ValueError:
            self.radius = None
            return self.__return_stock()
        coords = Zipcode.objects.filter(code=self.zipcode).first().centroid.point
        if not coords:
            return self.__return_stock()
        self.selected = True
        expression = f'radius={self.radius}*{self.zipcode}'
        name = f'Within {self.radius} mi.'
        self.enabled_values.append(BaseReturnValue(expression, name, None, True).asdict())
        prods = Product.objects.filter(locations__distance_lte=(coords, radius))
        self.queryset = prods.values_list('pk', flat=True)
        return prods


    def __filter_numeric(self):
        args = {}
        if self.selected_max:
            self.enabled_values.append(BaseReturnValue(f'{self.name}_max={self.selected_max}', f'Max {self.name}', None, True))
            args.update({f'{self.attribute}__lte': self.selected_max})
        if self.selected_min:
            self.enabled_values.append(BaseReturnValue(f'{self.name}_min={self.selected_min}', f'Min {self.name}', None, True))
            args.update({f'{self.attribute}__gte': self.selected_min})
        if self.attribute == 'low_price':
            qset = Product.objects.all().product_prices()
            self.queryset = qset.filter(**args).values_list('pk', flat=True)
        else:
            self.queryset = self.model.objects.filter(**args).values_list('pk', flat=True)
        return Product.objects.filter(pk__in=self.queryset)


    def filter_self(self):

        if self.field_type in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:
            return self.__filter_numeric()

        if self.field_type == 'CharField':
            return self.__filter_charfield()

        if self.field_type == 'BooleanField':
            return self.__filter_boolean()

        if self.field_type == 'MultiPointField':
            return self.__filter_radius()

        raise Exception(f'invalid field type -- {self.field_type}')


    def __parse_numeric(self, params: QueryDict):
        if self.dynamic:
            try:
                self.selected_min = params.pop(f'{self.name}_min')
                self.selected_max = params.pop(f'{self.name}_max')
                return params
            except KeyError:
                return params
        try:
            self.selected_min = params.get(f'{self.name}_min')
            self.selected_max = params.get(f'{self.name}_max')
            return params
        except KeyError:
            return params


    def __parse_radius(self, params: QueryDict):
        try:
            arg = params.pop('radius')
            self.radius, self.zipcode = arg.split('*')
            return params
        except (KeyError, IndexError):
            return params


    def parse_request(self, params: QueryDict):
        self.return_values = []
        self.enabled_values = []
        self.qterms = []
        print(self.field_type, self.name)
        if self.field_type in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:
            return self.__parse_numeric(params)

        if self.field_type in ['MultiPointField']:
            return self.__parse_radius(params)

        qterms = params.getlist(self.name, None)
        qterms = qterms[0].split(',') if qterms else []
        if self.attribute:
            values = list(self.model.objects.values_list(self.attribute, flat=True).distinct())
        else:
            values = self.attribute_list
        self.qterms = [term for term in qterms if term in values]
        return params


    def __calc_intersections(self, products, others):
        for facet in others:
            products = products.filter(pk__in=facet)
        return products


    def get_intersection(self, query_index_pk, products, others: List[QuerySet]):
        if self.dynamic:
            return self.__calc_intersections(products, others)
        cached_others: FacetOthersCollection = FacetOthersCollection.objects.filter(query_index__pk=query_index_pk, facet=self).first()
        if cached_others:
            return cached_others.products
        others = self.__calc_intersections(products, others)
        add_facet_others_delay.delay(query_index_pk, self.pk, list(others.values_list('pk', flat=True)))
        return others


    def __count_bools(self, query_index_pk, products, facets):
        _facets = [facet.queryset for facet in facets]
        others = self.get_intersection(query_index_pk, products, _facets)
        args = {value: models.Count(value, filter=models.Q(**{value: True})) for value in self.attribute_list}
        bool_values = others.aggregate(**args)
        for name, count in bool_values.items():
            selected = bool(name in self.qterms)
            expression = f'{self.name}={name}'
            return_value = BaseReturnValue(expression, name, count, selected)
            self.return_values.append(return_value)
            if selected:
                yield return_value.asdict()

                # self.enabled_values.append(return_value.asdict())

    def __count_inclusive(self, query_index_pk, products, facets):
        _facets = [facet.queryset for facet in facets if facet is not self]
        others = self.get_intersection(query_index_pk, products, _facets)
        values = others.values(self.attribute).annotate(val_count=models.Count(self.attribute))
        for val in values:
            name = val[self.attribute]
            count = val['val_count']
            selected = bool(name in self.qterms)
            expression = f'{self.name}={name}'
            return_value = BaseReturnValue(expression, name, count, selected)
            self.return_values.append(return_value)
            if selected:
                yield return_value.asdict()
                # self.enabled_values.append(return_value.asdict())

    def count_self(self, query_index_pk, products, facets):
        if self.field_type == 'MultiPointField':
            return None
        if self.field_type in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:
            if not self.dynamic:
                _facets = [facet.queryset for facet in facets]
                self.get_intersection(query_index_pk, products, _facets)
                return None
            return None
        if self.field_type == 'BooleanField':
            return self.__count_bools(query_index_pk, products, facets)
        return self.__count_inclusive(query_index_pk, products, facets)


    def serialize_self(self):
        return_dict = {
            'name': self.name,
            'selected': self.selected,
            'widget': self.widget,
            'editable': True,
            'all_values': [value.asdict() for value in self.return_values],
            }
        if self.field_type in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:
            abs_list = self.__get_absolutes()
            return_dict.update({'abs_min': abs_list[1]})
            return_dict.update({'abs_max': abs_list[0]})
            return_dict.update({'selected_min': self.selected_min})
            return_dict.update({'selected_max': self.selected_max})
        if self.field_type == 'MultiPointField':
            return_dict.update({'radii': [5, 10, 25, 50, 100, 200]})
            return_dict.update({'zipcode': self.zipcode})
            return_dict.update({'radius': self.radius})
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
        unique_together = ('query_dict', 'query_path')

    def __str__(self):
        return f'{self.query_path}_{self.query_dict}'


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


    # def __set_intersection(self, query_index_pk, products: QuerySet, *querysets: List[QuerySet]):
    #     self.others_intersection = products.intersection(*querysets).values_list('pk', flat=True)
    #     add_facet_others_delay.delay(query_index_pk, self.pk, list(self.others_intersection))
    #     return self.others_intersection
            # self.others_intersection = products.intersection(*others).values_list('pk', flat=True)
            # return self.others_intersection
        #     return others.values_list('products__pk', flat=True)

        # return self.__set_intersection(query_index_pk, products, *others)

    # def get_fresh_qs(self):
    #     pks = self.get_product_pks()
    #     prod_type = self.query_index.product_filter.get_content_model()
    #     return prod_type.objects.filter(pk__in=pks)




        # if self.others_intersection:
        #     return self.others_intersection
            # opks = list(products.intersection(*others).values_list('pk', flat=True))
            # self.others_intersection = products.filter(pk__in=opks)
            # return self.others_intersection
            # self.others_intersection = products.filter(pk__in=opks)
        # others = list(products.intersection(*others).values_list('pk', flat=True))
            # opks = list(cached_others.values_list('pk', flat=True))



        # if self.allow_multiple:
        # qterms = params.get(self.name, None)
        # self.qterms = [qterms] if qterms else []
        # return params



    # def parse_request(self, params: QueryDict):
    #     raise Exception('Facet must be subclassed!')


    # def filter_self(self, products: QuerySet):
    #     raise Exception('Facet must be subclassed!')

    # def serialize_self(self):
    #     return None

    # def enabled_values(self):
    #     raise Exception('Facet must be subclassed!')


        # if self.field_type == 'Charfield':
        #     pass

        # if self.field_type == 'BooleanField':
        #     pass

        # if self.field_type == 'MultiPointField':
        #     pass

        # if not self.dynamic:
        #     self.values = [val.asdict() for val in values]


# class BaseSingleFacet(BaseFacet):

#     def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
#         if not self.attribute:
#             raise Exception(f'must provide attribute for {self.name} facet')
#         if self.attribute == 'low_price':
#             return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
#         field = self.model._meta.get_field(self.attribute)
#         actual_type = field.get_internal_type()
#         if not self.field_type in field.get_internal_type():
#             raise Exception(f'Attribute -{self.attribute}\'s- field type {actual_type} != {self.field_type}')
#         if not self.name:
#             self.name = self.attribute
#         return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

#     class Meta:
#         abstract = True


# class BaseNumericFacet(BaseSingleFacet):
#     tick = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal(1.00))
#     abs_min = None
#     abs_max = None
#     selected_min = None
#     selected_max = None
#     message = None
#     enabled_values = []

#     class Meta:
#         abstract = True

#     def __get_absolutes(self):
#         if self.abs_max and self.abs_min:
#             return [self.abs_max, self.abs_min]
#         absolutes = self.others_intersection.aggregate(Min(self.attribute), Max(self.attribute))
#         self.abs_min = absolutes.get(f'{self.attribute}__min')
#         self.abs_max = absolutes.get(f'{self.attribute}__max')
#         if not self.dynamic:
#             self.save()
#         return [self.abs_max, self.abs_min]


#     def parse_request(self, params: QueryDict):
#         try:
#             self.selected_min = params.pop(f'{self.name}_min')
#             self.selected_max = params.pop(f'{self.name}_max')
#             return params
#         except KeyError:
#             return params


#     def filter_self(self, products: QuerySet):
#         args = {}
#         if self.selected_max:
#             self.enabled_values.append(BaseReturnValue(f'{self.name}_max={self.selected_max}', f'Max {self.name}', None, True))
#             args.update({f'{self.attribute}__lte': self.selected_max})
#         if self.selected_min:
#             self.enabled_values.append(BaseReturnValue(f'{self.name}_min={self.selected_min}', f'Min {self.name}', None, True))
#             args.update({f'{self.attribute}__gte': self.selected_min})
#         self.queryset = products.filter(**args)
#         return self.queryset

#     def count_self(self, query_index_pk, products, facets):
#         _facets = [facet.queryset for facet in facets if facet is not self]
#         self.get_intersection(query_index_pk, products, _facets)
#         return super().count_self(query_index_pk, products, facets)


#     def serialize_self(self):
#         abs_list = self.__get_absolutes()
#         return {
#             'name': self.name,
#             'selected': self.selected,
#             'editable': False,
#             'widget': 'range',
#             'abs_min': abs_list[1],
#             'abs_max': abs_list[0],
#             'selected_min': self.selected_min,
#             'selected_max': self.selected_max
#             }


# class MultiFacet(BaseSingleFacet):

#     field_type = 'CharField'
#     qterms: List[str] = None
#     allow_multiple = models.BooleanField(default=True)
#     widget = models.CharField(max_length=30, default='checkbox')
#     all_values: List[BaseReturnValue] = None
#     enabled_values: List[BaseReturnValue] = None


#     def parse_request(self, params: QueryDict):
#         if self.allow_multiple:
#             qterms = params.getlist(self.name, [])
#             qterms = qterms[0].split(',') if qterms else []
#             values = list(self.model.objects.values_list(self.attribute, flat=True).distinct())
#             self.qterms = [term for term in qterms if term in values]
#             return params
#         qterms = params.get(self.name, None)
#         self.qterms = [qterms] if qterms else []
#         return params


#     def filter_self(self, products: QuerySet):
#         if not self.qterms:
#             self.queryset = products
#             return self.queryset
#         q_object = models.Q()
#         for term in self.qterms:
#             q_object |= models.Q(**{self.attribute: term})
#             self.selected = True
#         self.queryset = products.filter(q_object)
#         return self.queryset


#     def count_self(self, query_index_pk, products, facets):
#         _facets = [facet.queryset for facet in facets if facet is not self]
#         others = self.get_intersection(query_index_pk, products, _facets)
#         values = others.values(self.attribute).annotate(val_count=models.Count(self.attribute))
#         self.all_values = []
#         self.enabled_values = []
#         for val in values:
#             name = val[self.attribute]
#             count = val['val_count']
#             selected = bool(name in self.qterms)
#             expression = f'{self.name}={name}'
#             return_value = BaseReturnValue(expression, name, count, selected)
#             self.all_values.append(return_value)
#             if selected:
#                 self.enabled_values.append(return_value.asdict())
#             # return return_value


#             # 'enabled_values': [value.asdict() for value in self.enabled_values]
#     def serialize_self(self):
#         return {
#             'name': self.name,
#             'selected': self.selected,
#             'widget': self.widget,
#             'editable': True,
#             'all_values': [value.asdict() for value in self.all_values],
#             'editable': False,
#             'abs_min': abs_list[1],
#             'abs_max': abs_list[0],
#             'radii': [5, 10, 25, 50, 100, 200],
#             'zipcode': self.zipcode,
#             'editable': False,
#             'radius': self.radius,
#             'selected_min': self.selected_min,
#             'selected_max': self.selected_max
#             }


# class BoolFacet(BaseFacet):

#     field_type = 'BooleanField'
#     qterms: List[str] = None
#     all_values: List[BaseReturnValue] = None
#     enabled_values: List[BaseReturnValue] = None



#     def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
#         if not self.attribute_list:
#             raise Exception(f'must provide attribute for {self.name} facet')
#         for attr in self.attribute_list:
#             field = self.model._meta.get_field(attr)
#             actual_type = field.get_internal_type()
#             if self.field_type != field.get_internal_type():
#                 raise Exception(f'Attribute -{attr}\'s- field type {actual_type} != {self.field_type}')
#         return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

#     @property
#     def values(self):
#         return list(self.attribute_list)


#     @property
#     def query_terms(self):
#         return self.qterms


#     def parse_request(self, params: QueryDict):
#         qterms = params.getlist(self.name)
#         self.qterms = [term for term in qterms if term in list(self.attribute_list)]
#         return params


#     def filter_self(self, products: QuerySet):
#         if not self.qterms:
#             self.queryset = products
#             return products
#         terms = {}
#         for term in self.qterms:
#             terms[term] = True
#             self.selected = True
#         self.queryset = products.filter(**terms)
#         return self.queryset


#     def count_self(self, query_index_pk, products, facets):
#         _facets = [facet.queryset for facet in facets]
#         others = self.get_intersection(query_index_pk, products, _facets)
#         args = {value: models.Count(value, filter=models.Q(**{value: True})) for value in self.values}
#         bool_values = others.aggregate(**args)
#         self.all_values = []
#         self.enabled_values = []
#         for name, count in bool_values.items():
#             selected = bool(name in self.query_terms)
#             expression = f'{self.name}={name}'
#             return_value = BaseReturnValue(expression, name, count, selected)
#             self.all_values.append(return_value)
#             if selected:
#                 self.enabled_values.append(return_value.asdict())


#     def serialize_self(self):
#         return {
#             'name': self.name,
#             'selected': self.selected,
#             'widget': 'checkbox',
#             'editable': False,
#             'all_values': [value.asdict() for value in self.all_values],
#             }


# class NonNullFacet(BaseFacet):

#     field_type = 'any'
#     qterms: List[str] = None
#     all_values: List[BaseReturnValue] = None
#     enabled_values: List[BaseReturnValue] = None


#     def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
#         if not self.attribute_list:
#             raise Exception(f'must provide attribute for {self.name} facet')
#         for attr in self.attribute_list:
#             self.model._meta.get_field(attr)
#         return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

#     @property
#     def values(self):
#         return list(self.attribute_list)


#     @property
#     def query_terms(self):
#         return self.qterms


#     def parse_request(self, params: QueryDict):
#         qterms = params.getlist(self.name)
#         self.qterms = [term for term in qterms if term in list(self.attribute_list)]
#         return params


#     def filter_self(self, products: QuerySet):
#         if not self.qterms:
#             self.queryset = products
#             return products
#         terms = {}
#         for term in self.qterms:
#             key = f'{term}__isnull'
#             terms[key] = False
#             self.selected = True
#         self.queryset = products.filter(**terms)
#         return self.queryset


#     def count_self(self, query_index_pk, products, facets):
#         _facets = [facet.queryset for facet in facets]
#         others = self.get_intersection(query_index_pk, products, _facets)
#         args = {value: models.Count(value, filter=models.Q(**{f'{value}__isnull': False})) for value in self.values}
#         bool_values = others.aggregate(**args)
#         self.all_values = []
#         self.enabled_values = []
#         for name, count in bool_values.items():
#             selected = bool(name in self.query_terms)
#             expression = f'{self.name}={name}'
#             return_value = BaseReturnValue(expression, name, count, selected)
#             self.all_values.append(return_value)
#             if selected:
#                 self.enabled_values.append(return_value.asdict())


#     def serialize_self(self):
#         return {
#             'name': self.name,
#             'selected': self.selected,
#             'widget': 'checkbox',
#             'editable': False,
#             'all_values': [value.asdict() for value in self.all_values],
#             }


# class RadiusFacet(BaseFacet):

#     field_type = 'MultiPointField'
#     radius = None
#     zipcode = None
#     enabled_values: List[BaseReturnValue] = None


#     def parse_request(self, params: QueryDict):
#         try:
#             arg = params.pop('radius')
#             self.radius, self.zipcode = arg.split('*')

#             return params
#         except (KeyError, IndexError):
#             return params


#     def filter_self(self, products: QuerySet):
#         self.enabled_values = []
#         if not (self.radius and self.zipcode):
#             self.queryset = products
#             return products
#         try:
#             radius = D(mi=int(self.radius))
#         except ValueError:
#             self.radius = None
#             self.queryset = products
#             return products
#         coords = Zipcode.objects.filter(code=self.zipcode).first().centroid.point
#         if coords:
#             self.queryset = products
#             return products
#         self.selected = True
#         expression = f'radius={self.radius}*{self.zipcode}'
#         name = f'Within {self.radius} mi.'
#         self.enabled_values.append(BaseReturnValue(expression, name, None, True).asdict())
#         self.queryset = products.filter(locations__distance_lte=(coords, radius))
#         return self.queryset


#     def serialize_self(self):
#         return {
#             'name': self.name,
#             'selected': self.selected,
#             'widget': 'radius',
#             'radii': [5, 10, 25, 50, 100, 200],
#             'zipcode': self.zipcode,
#             'editable': False,
#             'radius': self.radius,
#         }



# class DynamicRangeFacet(BaseNumericFacet):

#     field_type = 'RangeField'
#     dynamic = True


# class DynamicDecimalFacet(BaseNumericFacet):

#     field_type = 'DecimalField'
#     dynamic = True


# class StaticRangeFacet(BaseNumericFacet):

#     abs_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
#     abs_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
#     field_type = 'RangeField'


# class StaticDecimalFacet(BaseNumericFacet):

#     abs_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
#     abs_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
#     field_type = 'DecimalField'


# concrete specific facets below


    # @property
    # def values(self):
    #     products = self.model.objects.all()
    #     return products.aggregate(Min(self.attribute), Max(self.attribute))


    # @property
    # def query_terms(self):
    #     return [self.selected_min, self.selected_max]


    # @property
    # def abs_min(self):
    #     if self._abs_min:
    #         return self.abs_min
    #     self._abs_min = self.values.get(f'{self.attribute}__min', None)
    #     return self._abs_min


    # @property
    # def abs_max(self):
    #     if self._abs_max:
    #         return self.abs_max
    #     self._abs_min = self.values.get(f'{self.attribute}__max', None)
    #     return self._abs_max


# @dataclass
# class FacetValue:
#     """ datastructure for facet value
#         FacetValue(value: str, count: int, enabled: bool)
#     """
#     value: str = None
#     count: int = None
#     enabled: bool = False
#     remove_full: bool = True



# @dataclass
# class RangeFacetValue(FacetValue):
#     abs_min: str = None
#     abs_max: str = None
#     selected_min: str = None
#     selected_max: str = None



# @dataclass
# class LocationFacetValue(FacetValue):
#     default_radii: List[int] = None
#     zipcode: str = None
#     radius: int = 10


# @dataclass
# class Facet:
#     """ data structure for filter
#         Facet(name: str, facet_type: str, quer_value, values: [str])
#      """
#     name: str
#     facet_type: str
#     values: List = dfield(default_factory=lambda: [])
#     order: int = 10
#     key: bool = False
#     selected: bool = False
#     # total_count: int = 0
#     # qterms: List[str] = None
#     # queryset: QuerySet = None
#     # intersection: QuerySet = None
#     # collection_pk: str = None
#     return_values: List = dfield(default_factory=lambda: [])

    # @property
    # def values(self):
    #     raise Exception('Facet must be subclassed!')

    # @property
    # def widget(self):
    #     if self.widget:
    #         return self.widget
    #     return 'checkbox'

    # @property
    # def query_terms(self):
    #     raise Exception('Facet must be subclassed!')

        # def get_products(self, select_related=None):
    #     model = self.product_filter.get_content_model()
    #     pks = self.products.all().values_list('pk', flat=True)
    #     if select_related:
    #         return model.objects.select_related(select_related).filter(pk__in=pks)
    #     return model.objects.filter(pk__in=pks)
    # facet_name = models.CharField(max_length=100)

    
#         if not self.attribute:
#             raise Exception(f'must provide attribute for {self.name} facet')
#         if self.attribute == 'low_price':
#             return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
#         field = self.model._meta.get_field(self.attribute)
#         actual_type = field.get_internal_type()
#         if not self.field_type in field.get_internal_type():
#             raise Exception(f'Attribute -{self.attribute}\'s- field type {actual_type} != {self.field_type}')
#         if not self.name:
#             self.name = self.attribute
#         return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

