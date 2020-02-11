import uuid
from decimal import Decimal
from typing import List
from django.db import models
from django.db.models import Min, Max
from django.db.models.query import QuerySet
from django.http import QueryDict
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields
from django.contrib.gis.measure import D
from Addresses.models import Zipcode
from Suppliers.models import SupplierLocation
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
            'value': self.value
            }


class BaseFacet(models.Model):
    name = models.CharField(max_length=20, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    attribute = models.CharField(max_length=60, null=True, blank=True)
    attribute_list = pg_fields.ArrayField(
        models.CharField(max_length=60, null=True, blank=True)
        )

    dynamic = False
    selected = False
    field_type = 'CharField'

    queryset: QuerySet = None
    others_intersection: List[uuid.UUID] = None


    class Meta:
        unique_together = ('attribute', 'content_type', 'attribute_list')

    @property
    def model(self) -> models.Model:
        return self.content_type.model_class()

    def __set_intersection(self, query_index_pk, products: QuerySet, *querysets: List[QuerySet]):
        self.others_intersection = products.intersection(*querysets).values_list('pk', flat=True)
        add_facet_others_delay.delay(query_index_pk, self.pk, list(self.others_intersection))
        return self.others_intersection

    def get_intersection(self, query_index_pk, products, *others: List[QuerySet]):
        if self.others_intersection:
            return self.others_intersection
        others = FacetOthersCollection.objects.filter(query_index__pk=query_index_pk, facet_name=self).first()
        if others:
            return others.values_list('products__pk', flat=True)
        return self.__set_intersection(query_index_pk, products, *others)

    def parse_request(self, params: QueryDict):
        raise Exception('Facet must be subclassed!')

    def count_self(self, query_index_pk, products, *facets):
        return

    def filter_self(self, products: QuerySet):
        raise Exception('Facet must be subclassed!')

    def serialize_self(self):
        return None

    def enabled_values(self):
        raise Exception('Facet must be subclassed!')



class BaseSingleFacet(BaseFacet):

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.attribute:
            raise Exception(f'must provide attribute for {self.name} facet')
        field = self.model._meta.get_field(self.attribute)
        actual_type = field.get_internal_type()
        if self.field_type != field.get_internal_type():
            raise Exception(f'Attribute -{self.attribute}\'s- field type {actual_type} != {self.field_type}')
        if not self.name:
            self.name = self.attribute
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta:
        abstract = True



class BaseNumericFacet(BaseSingleFacet):
    tick = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal(1.00))
    abs_min = None
    abs_max = None
    selected_min = None
    selected_max = None
    message = None
    enabled_values = []

    class Meta:
        abstract = True

    def __get_absolutes(self):
        if self.abs_max and self.abs_min:
            return [self.abs_max, self.abs_min]
        absolutes = self.model.objects.aggregate(Min(self.attribute), Max(self.attribute))
        if not self.dynamic:
            self.save()
            abs_min = absolutes.get(f'{self.attribute}__min')
            abs_max = absolutes.get(f'{self.attribute}__max')
            return [abs_max, abs_min]


    def parse_request(self, params: QueryDict):
        try:
            self.selected_min = params.pop(f'{self.name}_min')
            self.selected_max = params.pop(f'{self.name}_max')
            return params
        except KeyError:
            return params


    def filter_self(self, products: QuerySet):
        args = {}
        if self.selected_max:
            self.enabled_values.append(BaseReturnValue(f'{self.name}_max={self.selected_max}', f'Max {self.name}'))
            args.update({f'{self.attribute}__lte': self.selected_max})
        if self.selected_min:
            self.enabled_values.append(BaseReturnValue(f'{self.name}_min={self.selected_min}', f'Min {self.name}'))
            args.update({f'{self.attribute}__gte': self.selected_min})
        self.queryset = products.filter(**args)
        return self.queryset


    def serialize_self(self):
        abs_list = self.__get_absolutes()
        return {
            'name': self.name,
            'selected': self.selected,
            'widget': 'range',
            'abs_min': abs_list[1],
            'abs_max': abs_list[0],
            'selected_min': self.selected_min,
            'selected_max': self.selected_max
            }




class MultiFacet(BaseSingleFacet):

    field_type = 'CharField'
    qterms: List[str] = None
    all_values: List[BaseReturnValue] = []
    enabled_values: List[BaseReturnValue] = []

    class Meta:
        abstract = True

    def parse_request(self, params: QueryDict):
        qterms = params.getlist(self.name, [])
        if qterms:
            qterms = qterms.split(',')
        values = self.model.objects.values_list(self.attribute, flat=True).distinct()
        self.qterms = [term for term in qterms if term in values]
        return params


    def filter_self(self, products: QuerySet):
        if not self.qterms:
            self.queryset = products
            return self.queryset
        for term in self.qterms:
            q_object |= models.Q(**{self.attribute: term})
            self.selected = True
        self.queryset = products.filter(q_object)
        return self.queryset


    def count_self(self, query_index_pk, products, *facets):
        _facets = [facet.queryset for facet in facets if facet is not self]
        others = self.get_intersection(query_index_pk, products, *_facets)
        values = others.values(self.attribute).annotate(val_count=models.Count(self.attribute))
        for val in values:
            name = val[self.attribute]
            count = val['val_count']
            selected = bool(name in self.qterms)
            expression = f'{self.name}={name}'
            return_value = BaseReturnValue(expression, name, count, selected)
            self.all_values.append(return_value)
            if selected:
                self.enabled_values.append(return_value)


    def serialize_self(self):
        return {
            'name': self.name,
            'selected': self.selected,
            'widget': 'checkbox',
            'all_values': [value.asdict() for value in self.all_values],
            # 'enabled_values': [value.asdict() for value in self.enabled_values]
            }



class BoolFacet(BaseFacet):

    field_type = 'BooleanField'
    qterms: List[str] = None
    all_values: List[BaseReturnValue] = []
    enabled_values: List[BaseReturnValue] = []



    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.attribute_list:
            raise Exception(f'must provide attribute for {self.name} facet')
        for attr in self.attribute_list:
            field = self.model._meta.get_field(attr)
            actual_type = field.get_internal_type()
            if self.field_type != field.get_internal_type():
                raise Exception(f'Attribute -{attr}\'s- field type {actual_type} != {self.field_type}')
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @property
    def values(self):
        return list(self.attribute_list)


    @property
    def query_terms(self):
        return self.qterms


    def parse_request(self, params: QueryDict):
        qterms = params.getlist(self.name)
        self.qterms = [term for term in qterms if term in list(self.attribute_list)]
        return params


    def filter_self(self, products: QuerySet):
        if not self.qterms:
            self.queryset = products
            return products
        terms = {}
        for term in self.qterms:
            terms[term] = True
            self.selected = True
        self.queryset = products.filter(**terms)
        return self.queryset


    def count_self(self, query_index_pk, products, *facets):
        _facets = [facet.queryset for facet in facets]
        others = self.get_intersection(query_index_pk, products, *_facets)
        args = {value: models.Count(value, filter=models.Q(**{value: True})) for value in self.values}
        bool_values = others.aggregate(**args)
        for name, count in bool_values.items():
            selected = bool(name in self.query_terms)
            expression = f'{self.name}={name}'
            return_value = BaseReturnValue(expression, name, count, selected)
            self.all_values.append(return_value)
            if selected:
                self.enabled_values.append(return_value)

    def serialize_self(self):
        return {
            'name': self.name,
            'selected': self.selected,
            'widget': 'checkbox',
            'all_values': [value.asdict() for value in self.all_values],
            # 'enabled_values': [value.asdict() for value in self.enabled_values]
            }




class RadiusFacet(BaseFacet):

    field_type = 'MultiPointField'
    radius = None
    zipcode = None
    enabled_value: BaseReturnValue = None


    def parse_request(self, params: QueryDict):
        try:
            arg = params.pop('radius')
            self.radius, self.zipcode = arg.split('*')

            return params
        except (KeyError, IndexError):
            return params


    def filter_self(self, products: QuerySet):
        if not (self.radius and self.zipcode):
            self.queryset = products
            return products
        try:
            radius = D(mi=int(self.radius))
        except ValueError:
            self.radius = None
            self.queryset = products
            return products
        coords = Zipcode.objects.filter(code=self.zipcode).first().centroid.point
        if coords:
            self.queryset = products
            return products
        self.selected = True
        expression = f'radius={self.radius}*{self.zipcode}'
        name = f'Within {self.radius} mi.'
        self.enabled_value = BaseReturnValue(expression, name)
        self.queryset = products.filter(locations__distance_lte=(coords, radius))
        return self.queryset

    def serialize_self(self):
        return {
            'name': self.name,
            'selected': self.selected,
            'widget': 'radius',
            'radii': [5, 10, 25, 50, 100, 200],
            'zipcode': self.zipcode,
            'radius': self.radius,
        }


class DynamicRangeFacet(BaseNumericFacet):

    field_type = 'RangeField'
    dynamic = True



class DynamicDecimalFacet(BaseNumericFacet):

    field_type = 'DecimalField'
    dynamic = True



class StaticRangeFacet(BaseNumericFacet):

    abs_min = pg_fields.ArrayField(
        models.DecimalField(max_digits=8, decimal_places=2)
        )
    abs_max = pg_fields.ArrayField(
        models.DecimalField(max_digits=8, decimal_places=2)
        )
    field_type = 'RangeField'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)



class StaticDecimalFacet(BaseNumericFacet):

    abs_min = models.DecimalField(max_digits=8, decimal_places=2)
    abs_max = models.DecimalField(max_digits=8, decimal_places=2)
    field_type = 'DecimalField'



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

    # def get_fresh_qs(self):
    #     pks = self.get_product_pks()
    #     prod_type = self.query_index.product_filter.get_content_model()
    #     return prod_type.objects.filter(pk__in=pks)


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