import uuid
import numpy
import functools
import itertools
import urllib
from decimal import Decimal
from dataclasses import dataclass, asdict
from dataclasses import field as dfield
from typing import List, Tuple
from django.db import models, transaction
from django.core.exceptions import FieldError
# from django.db.models.functions import Upper, Lower, Least, Cast, Coalesce
from django.db.models import Min, Max, Subquery, Count, Q
from django.urls import resolve as dj_resolve
from django.contrib.postgres.search import SearchVector
from django.contrib.gis.measure import D
from django.db.models.query import QuerySet
from django.http import HttpRequest, QueryDict
# from django.core import exceptions
# from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields
from config.scripts.globals import valid_subclasses
from Addresses.models import Zipcode
from Products.serializers import SerpyProduct
from Products.models import Product, ProductSubClass
from UserProducts.serializers import RetailerProductMiniSerializer
from UserProducts.models import RetailerProduct
from UserProductCollections.models import RetailerLocation


AVAILABILITY_FACET = 'AvailabilityFacet'
BOOLGROUP_FACET = 'BoolGroupFacet'
COLOR_FACET = 'ColorFacet'
DEPENDENT_FACET = 'DependentFacet'
KEYTERM_FACET = 'KeyTermFacet'
LOCATION_FACET = 'LocationFacet'
MANUFACTURER_FACET = 'ManufacturerFacet'
MULTITEXT_FACET = 'MultiTextFacet'
PRICE_FACET = 'PriceFacet'
RANGE_FACET = 'RangeFacet'


def return_radii():
    return [5, 10, 15, 25, 50, 100]


@dataclass
class FacetValue:
    """ datastructure for facet value
        FacetValue(value: str, count: int, enabled: bool)
    """
    value: str = None
    count: int = None
    enabled: bool = False


@dataclass
class RangeFacetValue(FacetValue):
    abs_min: str = None
    abs_max: str = None
    selected_min: str = None
    selected_max: str = None


@dataclass
class LocationFacet(FacetValue):
    default_radii: List[int] = dfield(default_factory=return_radii)
    zipcode: str = None
    radius: int = 10


@dataclass
class Facet:
    """ data structure for filter
        Facet(name: str, facet_type: str, quer_value, values: [str])
     """
    name: str
    facet_type: str
    quer_value: str
    values: List = dfield(default_factory=lambda: [])
    order: int = 10
    key: bool = False
    selected: bool = False
    total_count: int = 0
    qterms: List[str] = None
    queryset: QuerySet = None
    intersection: QuerySet = None
    collection_pk: str = None
    return_values: List = dfield(default_factory=lambda: [])


def get_absolute_range(products: QuerySet, facet: Facet):
    values = products.aggregate(Min(facet.quer_value), Max(facet.quer_value))
    print(values)
    min_val = values.get(f'{facet.quer_value}__min', None)
    max_val = values.get(f'{facet.quer_value}__max', None)
    print(min_val, max_val)
    if not (min_val or max_val):
        return facet
    if min_val == max_val:
        return facet
    return_value = RangeFacetValue()
    return_value.count = 1
    return_value.value = facet.name
    return_value.abs_max = str(max_val)
    return_value.selected_max = str(max_val)
    return_value.abs_min = str(min_val)
    return_value.selected_min = str(min_val)
    facet.return_values = [return_value]
    return facet


def complete_range(products: QuerySet, quer_value, query, direction: str):
    qrange = Decimal(query[-1])
    direction_transform = {'min': 'gte', 'max': 'lte'}
    argument = {f'{quer_value}__{direction_transform[direction]}': qrange}
    return products.filter(**argument)


def construct_range_facet(products: QuerySet, facet: Facet):
    if not facet.return_values:
        facet = get_absolute_range(products, facet)
    if not facet.return_values:
        return (products, facet, False)
    facet.total_count = 1
    if not facet.qterms:
        return (products, facet, True)
    facet_value = facet.return_values[-1]
    min_query = [q.replace('min-', '') for q in facet.qterms if 'min' in q]
    max_query = [q.replace('max-', '') for q in facet.qterms if 'max' in q]
    facet.qterms = []
    if min_query:
        facet.qterms.append(f'min-{min_query[-1]}')
        products = complete_range(products, facet.quer_value, min_query, 'min')
        facet_value.selected_min = min_query[-1]
        facet.total_count += 1
        facet_value.enabled = True
        facet.selected = True
    if max_query:
        facet.qterms.append(f'max-{max_query[-1]}')
        products = complete_range(products, facet.quer_value, max_query, 'max')
        facet_value.selected_max = max_query[-1]
        facet.total_count += 1
        facet_value.enabled = True
        facet.selected = True
    facet.return_values = [facet_value]
    return (products, facet, True)

class QueryIndexManager(models.Manager):
    def get_or_create_qi(self, **kwargs):
        query_dict = kwargs.get('query_dict')
        query_path = kwargs.get('query_path')
        product_filter = kwargs.get('product_filter')
        retailer_location = kwargs.get('retailer_location')
        args = {
            'query_dict': query_dict,
            'query_path': query_path,
            'product_filter': product_filter
            }
        if retailer_location:
            location = RetailerLocation.objects.get(pk=retailer_location)
            args['retailer_location'] = location
        query_index = self.model.objects.get_or_create(**args)
        return query_index


class QueryIndex(models.Model):
    """
    cache relating query strings to json responses
    """
    query_dict = models.CharField(max_length=1000)
    query_path = models.CharField(max_length=500)
    response = pg_fields.JSONField(null=True)
    dirty = models.BooleanField(default=True)
    retailer_location = models.ForeignKey(
        RetailerLocation,
        null=True,
        on_delete=models.CASCADE,
        related_name='qis'
        )
    product_filter = models.ForeignKey(
        'ProductFilter',
        on_delete=models.CASCADE,
        related_name='query_indexes'
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

    def refresh(self):
        """ DO NOT USE!
        this method should only ever be called by celery task.
        """
        view, args, kwargs = dj_resolve(self.query_path)
        request = HttpRequest()
        request.method = 'GET'
        request.path = self.query_path
        request.GET = QueryDict(self.query_dict)
        view(request, update=True, *args, **kwargs)

    def get_product_pks(self):
        return self.products.values_list('pk', flat=True)

    def get_products(self, select_related=None):
        model = self.product_filter.get_content_model()
        pks = self.products.all().values_list('pk', flat=True)
        if select_related:
            return model.objects.select_related(select_related).filter(pk__in=pks)
        return model.objects.filter(pk__in=pks)

    @classmethod
    def get_all_paths(cls):
        from UserProductCollections.models import RetailerLocation
        base = 'specialized-products/filter/'
        paths = [
            {'product_type': pt, 'path': base + pt.__name__}
            for pt in ProductSubClass.__subclasses__()
            ]
        locations = RetailerLocation.objects.all()
        for location in locations:
            location_list = [
                {'product_type': product_type['cls'],
                 'path': f'{base}{product_type["name"]}/{location.pk}'}
                for product_type in location.product_types(True)
                ]
            paths = paths + location_list
        return paths
        # location_list = [f'{base}{product_type["name"]}/{location.pk}' for product_type in location.product_types]
        # paths = [base + cls.__name__ for cls in ProductSubClass.__subclasses__()]

    @classmethod
    def get_all_queries(cls):
        product_types = [pt for pt in ProductSubClass.__subclasses__()]
        for p_type in product_types:
            p_filter = ProductFilter.get_filter(p_type)

    # need to write this method to create all possible queries for a given view
    @classmethod
    def get_all_combinations(cls):
        paths = cls.get_all_paths()


class FacetOthersCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    query_index = models.ForeignKey(QueryIndex, on_delete=models.CASCADE)
    facet_name = models.CharField(max_length=100)
    products = models.ManyToManyField(
        'Products.Product',
        related_name='facet_collections'
    )

    class Meta:
        unique_together = ('query_index', 'facet_name')

    def __str__(self):
        return f'{self.facet_name} {str(self.query_index)}'

    def assign_new_products(self, products):
        self.products.clear()
        self.products.add(*products)
        self.save()

    def get_fresh_qs(self):
        pks = self.get_product_pks()
        prod_type = self.query_index.product_filter.get_content_model()
        return prod_type.objects.filter(pk__in=pks)

    def get_product_pks(self):
        return self.products.values_list('pk', flat=True)


class ProductFilter(models.Model):
    """ Basic instance structure to set filter fields for product subclasses
        self cleaning: if field not in class, or not of proper type, will automatically
        be cleared from instance
    """
    facets = []
    content_model = None
    products: QuerySet = None
    sub_product = models.OneToOneField(
        ContentType,
        limit_choices_to={'app_label': 'SpecializedProducts'},
        on_delete=models.CASCADE,
        null=True
        )
    bool_groups = pg_fields.JSONField(blank=True, null=True)
    key_field = models.CharField(max_length=30, null=True, blank=True)
    color_field = models.CharField(max_length=30, null=True, blank=True)
    independent_multichoice_fields = pg_fields.ArrayField(
        models.CharField(max_length=30, blank=True),
        null=True,
        blank=True
        )
    independent_range_fields = pg_fields.ArrayField(
        models.CharField(max_length=30, blank=True),
        null=True,
        blank=True
        )
    dependent_fields = pg_fields.ArrayField(
        models.CharField(max_length=30, blank=True),
        null=True,
        blank=True
        )
    filter_dictionary = pg_fields.JSONField(blank=True, null=True)

    @classmethod
    def get_filter(cls, model: models.Model):
        content_type = ContentType.objects.get_for_model(model)
        prod_filter = cls.objects.filter(sub_product=content_type).first()
        if not prod_filter:
            raise Exception('No filter for this class')
        return prod_filter

    def produce_base_queries(self):

        def format_range(range_list):
            ranges = [range_list[0:i] for i in range(len(range_list))]
            return [urllib.parse.quote('&&'.join(r)) for r in ranges]

        all_queries = []
        multi_group_fields = [
            *self.independent_multichoice_fields,
            # *self.dependent_fields,
            # self.key_field,
            # self.color_field
            ]
        for group in self.bool_groups:
            group_vals = format_range(
                [f'{group["name"]}={value}' for value in group["values"]])
            all_queries.append(group_vals)
        for field in multi_group_fields:
            values = self.get_model_products().values_list(field, flat=True).distinct()
            group_val = format_range(
                [f'{field}={value}' for value in values if value])
            all_queries.append(group_val)
        all_queries = list(filter(None, all_queries))
        # full_list = list(itertools.product(*all_queries))
        total_queries = []
        for bar in all_queries:
            total_number = len(bar)
            example = bar[-1]
            triangle = sum(range(total_number))
            total_queries.append(triangle)
            print('total_number = ', str(total_number))
            print('example = ', example)
            print('triangle = ', str(triangle))
        total_queries = functools.reduce(lambda x, y: x*y, total_queries) 
        # 20,785,981,783,727,160 - thats how many queries exist. 20 quadrillion - have to improve
        print('all queries = ', str(total_queries))


    def get_content_model(self):
        """returns model associated with the ContentType instance in self.subproduct

        Returns:
            product.sub_class instance
        """
        if not self.content_model:
            self.content_model = self.sub_product.model_class()
        return self.content_model

    def floating_fields(self):
        """returns quer_values of facets that are never concretely set i.e price, location, ranges
        """
        print(self.independent_range_fields)
        return ['low_price', 'in_store_ppu', 'location', 'search', 'availability'] + self.independent_range_fields

    def get_model_products(self) -> QuerySet:
        """ Returns a queryset containing all product subclasses of model type for
        self.sub_product

        Returns:
            [queryset]
        """
        if not self.products:
            model = self.get_content_model()
            self.products = model.objects.all()
        return self.products

    def check_value(self, name, fieldnames: List[str] = None) -> Tuple[bool, str]:
        """ if fieldname is not passed in argument, returns tuple that:
        1. tells if 'name' is a field present on self.sub_product
        2. if so, what the django field type is for that field, else none

            if fieldname is passed as argument, returns tuple that
        1. tells if 'name' is present on the model and in the specified 'fieldnames'
        2. if so, the type of field, else none

        Arguments:
            name {str} -- name of the field to check

        Keyword Arguments:
            fieldnames {List[str]} -- fieldnames to check against (default: {None})

        Returns:
            Tuple[bool, str]
        """
        mymodel = self.get_content_model()
        fields = (field.name for field in mymodel._meta.get_fields())
        if name not in fields:
            return [False, None]
        field = mymodel._meta.get_field(name)
        field_type = field.get_internal_type()
        if fieldnames and field_type not in fieldnames:
            return [False, field_type]
        return [True, field_type]

    def check_bools(self):
        if not self.bool_groups:
            return
        valid_groups = []
        for group_count, group in sorted(enumerate(self.bool_groups), reverse=True):
            for key in list(group):
                if key not in ('values', 'name'):
                    del group[key]
            values = group.get('values', None)
            if not values:
                del self.bool_groups[group_count]
                continue
            valid_values = []
            for count, value in enumerate(values):
                if not self.check_value(value, ['BooleanField'])[0]:
                    del values[count]
                    continue
                valid_values.append(value)
            valid_groups.append(Facet(group['name'], BOOLGROUP_FACET, group['name'], valid_values, order=4))
        self.facets = self.facets + valid_groups

    def check_keyterm(self):
        try:
            values = self.get_model_products().values_list(self.key_field, flat=True).distinct()
            self.facets.append(
                Facet(
                    self.key_field,
                    KEYTERM_FACET,
                    self.key_field,
                    key=True,
                    values=list(filter(None, values)),
                    order=5
                    ))
        except FieldError:
            self.key_field = None
            return

    def check_mc_fields(self):
        indices = sorted(enumerate(self.independent_multichoice_fields), reverse=True)
        for count, standalone in indices:
            try:
                values = self.get_model_products().values_list(standalone, flat=True).distinct()
                self.facets.append(
                    Facet(
                        standalone,
                        MULTITEXT_FACET,
                        standalone,
                        values=list(filter(None, values)),
                        order=6
                        ))
            except FieldError:
                del self.independent_multichoice_fields[count]
                continue

    def check_range_fields(self):
        range_fields = [pg_fields.IntegerRangeField, pg_fields.DecimalRangeField]
        discreet_fields = [models.DecimalField, models.IntegerField]
        acceptable_field_types = [f.__name__ for f in range_fields + discreet_fields]
        for count, standalone in sorted(enumerate(self.independent_range_fields), reverse=True):
            check, field_type = self.check_value(standalone, acceptable_field_types)
            if not check:
                del self.independent_range_fields[count]
                continue
            self.get_range_values(standalone, standalone, count)

    def get_range_values(self, name, quer_value, facet_type=RANGE_FACET, order=7):
        values = get_absolute_range(self.get_model_products(), quer_value)
        if not values:
            return
        min_val, max_val = values
        range_value = RangeFacetValue(value=name, abs_min=str(min_val), abs_max=str(max_val))
        self.facets.append(Facet(name, facet_type, quer_value, order=order, total_count=1, return_values=[asdict(range_value)]))

    def check_color_field(self):
        check, fieldtype = self.check_value(self.color_field)
        if not check:
            self.color_field = None
            return
        values = self.get_model_products().values_list(self.color_field, flat=True).distinct()
        values = [v for v in values if v]
        self.facets.append(Facet('color', COLOR_FACET, self.color_field, values=values, order=10))

    def check_dependents(self):
        for count, dependent in sorted(enumerate(self.dependent_fields), reverse=True):
            if not self.check_value(dependent):
                del self.dependent_fields[count]
            values = self.get_model_products().values_list(dependent, flat=True).distinct()
            values = [v for v in values if v]
            self.facets.append(Facet(dependent, DEPENDENT_FACET, dependent, values=values))

    def add_product_facets(self):
        self.facets.append(
            Facet(
                'availability',
                AVAILABILITY_FACET,
                'availability',
                key=True,
                values=Product.objects.safe_availability_commands(), order=1)
            )
        manu_values = self.get_model_products().values_list('manufacturer__label', flat=True).distinct()
        self.facets.append(Facet('manufacturer', MANUFACTURER_FACET, 'manufacturer__label', list(manu_values), order=8))

    def check_fields(self):
        self.add_product_facets()
        self.check_bools()
        self.check_keyterm()
        self.check_range_fields()
        self.check_color_field()
        self.check_mc_fields()
        self.check_dependents()

    def add_filter_dictionary(self):
        self.filter_dictionary = [asdict(facet) for facet in self.facets]

    def invalidate_queries(self):
        for query_index in self.query_indexes.all():
            query_index.dirty = True
            query_index.save()

    @transaction.atomic()
    def save(self, *args, **kwargs):
        self.facets = []
        self.filter_dictionary = None
        self.check_fields()
        self.add_filter_dictionary()
        qis = self.query_indexes.all()
        qis.delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_content_model().__name__ + ' Filter'
