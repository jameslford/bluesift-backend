import uuid
from decimal import Decimal
from dataclasses import dataclass, asdict
from dataclasses import field as dfield
from typing import List, Tuple
from django.db import models, transaction
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
    collection_pk: uuid = None
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


def get_filter(model: models.Model):
    content_type = ContentType.objects.get_for_model(model)
    prod_filter = ProductFilter.objects.filter(sub_product=content_type).first()
    if not prod_filter:
        raise Exception('No filter for this class')
    return prod_filter


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


class QueryIndex(models.Model):
    """ cache relating query strings to json responses

    """
    query_dict = models.CharField(max_length=1000)
    query_path = models.CharField(max_length=500)
    response = pg_fields.JSONField(null=True)
    dirty = models.BooleanField(default=True)
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

    def get_products(self):
        model = self.product_filter.get_content_model()
        pks = self.products.all().values_list('pk', flat=True)
        return model.objects.filter(pk__in=pks)

    @classmethod
    def get_all_paths(cls):
        from UserProductCollections.models import RetailerLocation
        base = 'specialized-products/filter/'
        paths = [base + cls.__name__ for cls in ProductSubClass.__subclasses__()]
        locations = RetailerLocation.objects.all()
        for location in locations:
            location_list = [f'{base}{product_type["name"]}/{location.pk}' for product_type in location.product_types]
            paths = paths + location_list
        print(paths)
        return paths

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

    def assign_new_products(self, products: QuerySet):
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

    def get_model_products(self):
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
        check = self.check_value(self.key_field)
        if not check:
            self.key_field = None
            return
        products = self.get_model_products().values_list(self.key_field, flat=True).distinct()
        products = [v for v in products if v]
        self.facets.append(Facet(self.key_field, KEYTERM_FACET, self.key_field, key=True, values=products, order=5))

    def check_mc_fields(self):
        indices = sorted(enumerate(self.independent_multichoice_fields), reverse=True)
        for count, standalone in indices:
            check = self.check_value(standalone)[0]
            if not check:
                del self.independent_multichoice_fields[count]
                continue
            products = self.get_model_products().values_list(standalone, flat=True).distinct()
            products = [v for v in products if v]
            self.facets.append(Facet(standalone, MULTITEXT_FACET, standalone, values=products, order=6))

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

    def check_content_model(self):
        if self.sub_product in valid_subclasses():
            return False
        return True

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
        if not self.check_content_model():
            self.delete()
            return
        self.facets = []
        self.filter_dictionary = None
        self.check_fields()
        self.add_filter_dictionary()
        qis = self.query_indexes.all()
        qis.delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_content_model().__name__ + ' Filter'


@dataclass
class Message:
    main: str = 'No results'
    note: str = 'Please expand selection'


@dataclass
class FilterResponse:
    legit_queries: List[str] = dfield(default_factory=list)
    page: int = 1
    load_more: bool = True
    return_products: bool = True
    message: Message = None
    product_count: int = 0
    filter_dict: List[dict] = None
    products: List[dict] = None


class Sorter:
    """ takes a request and returns a filter and product set """
    def __init__(self, product_type: ProductSubClass, request: HttpRequest, update=False, location_pk=None):
        self.request: HttpRequest = request
        self.product_type = product_type
        self.product_filter: ProductFilter = get_filter(product_type)
        self.location_pk = location_pk
        self.page_size = 40
        self.update = update
        self.response: FilterResponse = FilterResponse()
        self.facets: List[Facet] = []
        self.query_index: QueryIndex = None

    @transaction.atomic()
    def __call__(self):
        return self.__process_request()

    def get_index_by_qv(self, keyword: str):
        for count, facet in enumerate(self.facets):
            facet: Facet = facet
            if facet.quer_value == keyword:
                return count
        print(keyword + ' not found in facets.')
        return None

    def get_indices_by_ft(self, facet_type: str) -> [int]:
        indices = []
        for count, facet in enumerate(self.facets):
            if facet.facet_type == facet_type:
                indices.append(count)
        return indices

    def __check_availability_facet(self, stripped_fields):
        avail_facet: Facet = self.facets[self.get_indices_by_ft(AVAILABILITY_FACET)[0]]
        qterms = stripped_fields.pop('availability') if 'availability' in stripped_fields else []
        avail_facet.qterms = [term for term in qterms if term in Product.objects.safe_availability_commands()]
        if self.location_pk:
            self.facets.append(Facet('retailer price', PRICE_FACET, 'in_store_ppu', total_count=1, order=2))
            return True
        if not avail_facet.qterms:
            return False
        self.facets.append(Facet('location', LOCATION_FACET, 'location', total_count=1, order=3))
        self.facets.append(Facet('price', PRICE_FACET, 'low_price', total_count=1, order=2))
        return True

    def get_products(self):
        if self.location_pk:
            pks = RetailerProduct.objects.filter(retailer__pk=self.location_pk).values_list('product__pk', flat=True)
            return self.product_type.objects.all().prefetch_related(
                'priced'
            ).filter(pk__in=pks)
        return self.product_type.objects.all()

    def __instantiate_facets(self):
        self.facets = []
        filter_dict = self.product_filter.filter_dictionary
        for f_dict in filter_dict:
            facet: Facet = Facet(**f_dict)
            self.facets.append(facet)

    def __check_dependents(self):
        kt_facet = self.get_indices_by_ft(KEYTERM_FACET)
        if kt_facet and self.facets[kt_facet[0]].qterms:
            return
        facet_indices = self.get_indices_by_ft(DEPENDENT_FACET)
        for index in sorted(facet_indices, reverse=True):
            del self.facets[index]

    def __process_request(self):
        if self.request.method != 'GET':
            self.response.message = 'Invalid request method'
            return asdict(self.response)
        stripped_fields = {}
        query_dict: QueryDict = QueryDict(self.request.GET.urlencode(), mutable=True)
        for field in self.product_filter.floating_fields():
            if field in query_dict:
                values = query_dict.pop(field)
                stripped_fields[field] = values
        query_index, created = QueryIndex.objects.get_or_create(
            query_path=self.request.path,
            query_dict=query_dict.urlencode(),
            product_filter=self.product_filter
            )
        self.query_index = query_index
        if query_index.dirty or self.update or created:
            print('building full ' + query_dict.urlencode())
            return self.build_full(stripped_fields)
        print('straight to floating ' + query_dict.urlencode())
        return self.filter_floating(stripped_fields)

    def filter_floating(self, stripped_fields: dict):
        print('stripped fields = ', stripped_fields)
        self.__instantiate_facets()
        self.__parse_querydict()
        if not stripped_fields:
            return self.__finalize_response(
                self.query_index.get_products().select_related('manufacturer').product_prices(self.location_pk)
                )
        print('stripped fields')
        self.__check_availability_facet(stripped_fields)
        products = self.get_products().product_prices(self.location_pk)
        search_terms = stripped_fields.pop('search') if 'search' in stripped_fields else None
        for key in stripped_fields:
            index = self.get_index_by_qv(key)
            if index is None:
                continue
            facet: Facet = self.facets[index]
            facet.qterms = stripped_fields[key]
        products = self.__filter_search_terms(products, search_terms)
        products = self.__filter_location(products)
        products = self.__filter_range(products)
        return self.__finalize_response(products, True)

    def __finalize_response(self, products: QuerySet, new_terms=False):
        if new_terms:
            avai_prods = products.select_related(
                'manufacturer'
            ).filter(pk__in=Subquery(self.query_index.get_products().values('pk')))
            avai_prods = self.__filter_availability(avai_prods)
            self.__count_objects(avai_prods)
            self.response.product_count = avai_prods.count()
            products = avai_prods.product_prices(self.location_pk)
            self.response.products = self.__serialize_products(products)
            self.__set_filter_dict()
            return asdict(self.response)
        products = self.__filter_availability(products)
        availability_facet = self.facets[self.get_index_by_qv('availability')]
        # products = products.product_prices(self.location_pk)
        product_count = products.count()
        self.response.product_count = product_count
        serialized_prods = self.__serialize_products(products)
        response = self.query_index.response
        response['product_count'] = product_count
        response['filter_dict'] = [asdict(availability_facet)] + response['filter_dict']
        response['products'] = serialized_prods
        return response
        # return asdict(self.response)
        # self.__count_objects(products)
        # self.response.product_count = products.count()
        # self.__set_filter_dict()

    def __parse_querydict(self):
        request_dict = QueryDict(self.query_index.query_dict)
        self.response.page = int(request_dict.get('page', 1))
        for facet in self.facets:
            qterms = request_dict.getlist(facet.quer_value, [])
            facet.qterms = [term for term in qterms if term in facet.values]
        self.__check_dependents()

    def build_full(self, stripped_fields=None):
        self.__instantiate_facets()
        products = self.get_products()
        self.__parse_querydict()
        self.__filter_bools(products)
        self.__filter_multi(products)
        self.__count_objects(products, True)
        indices = self.__get_counted_facet_indices()
        qsets = [self.facets[q].queryset for q in indices]
        products = products.intersection(*qsets)
        self.__set_filter_dict()
        self.query_index.products.clear()
        self.query_index.products.add(*products)
        self.query_index.response = asdict(self.response)
        self.query_index.dirty = False
        self.query_index.save()
        self.response = FilterResponse()
        return self.filter_floating(stripped_fields)
        # return self.__finalize_response(products)

    def __count_objects(self, products: QuerySet, new=False):
        indices = self.__get_counted_facet_indices()
        for index in indices:
            facet = self.facets[index]
            if not facet.queryset and new:
                self.__return_no_products()
                return
            new_prods = None
            foc, created = FacetOthersCollection.objects.get_or_create(
                query_index=self.query_index,
                facet_name=facet.name)
            if created:
                other_qsets = [self.facets[q].queryset for q in indices if q != index]
                intersection = [product.pk for product in products.intersection(*other_qsets)]
                new_prods = self.product_type.objects.filter(pk__in=intersection)
                foc.assign_new_products(new_prods)
            else:
                new_prods = products.filter(pk__in=foc.get_product_pks())
            return_values = []
            if facet.facet_type == BOOLGROUP_FACET:
                args = {value: Count(value, filter=Q(**{value: True})) for value in facet.values}
                bool_values = new_prods.aggregate(**args)
                for value in bool_values.items():
                    name, count = value
                    selected = bool(facet.qterms and name in facet.qterms)
                    facet.total_count += count
                    if selected:
                        facet.selected = True
                    return_values.append(FacetValue(name, count, selected))
                facet.return_values = return_values
                continue
            values = list(new_prods.values(facet.quer_value).annotate(val_count=Count(facet.quer_value)))
            for value in values:
                count = value['val_count']
                label = value[facet.quer_value]
                selected = bool(facet.qterms and label in facet.qterms)
                facet.total_count += count
                if selected:
                    facet.selected = True
                return_values.append(FacetValue(label, count, selected))
                facet.return_values = return_values

    def __serialize_products(self, products: QuerySet):
        if not self.response.return_products:
            return []
        start_page = self.response.page - 1
        product_start = start_page * self.page_size
        product_end = self.response.page * self.page_size
        if product_end > self.response.product_count:
            print('under page size. Product start = ' + str(product_start))
            self.response.load_more = False
            _products = products[product_start:]
            return SerpyProduct(_products, many=True, label=self.location_pk).data
        _products = products.all()[product_start:product_end]
        return SerpyProduct(_products, many=True).data

    def __set_filter_dict(self):
        for facet in self.facets:
            facet.queryset = None
            facet.values = []
            if facet.qterms:
                for term in facet.qterms:
                    self.response.legit_queries = [q for q in self.response.legit_queries] + [f'{facet.quer_value}={term}']
        self.facets.sort(key=lambda x: x.order)
        self.response.filter_dict = [asdict(qfacet) for qfacet in self.facets]

    def __filter_bools(self, products: QuerySet):
        bool_indices = self.get_indices_by_ft(BOOLGROUP_FACET)
        for index in bool_indices:
            facet = self.facets[index]
            if not facet.qterms:
                facet.qterms = []
                self.facets[index].queryset = products
                continue
            facet.qterms = [term for term in facet.qterms if term in facet.values]
            facet.selected = True
            q_object = models.Q()
            for term in facet.qterms:
                q_object |= models.Q(**{term: True})
                facet.selected = True
            facet.queryset = products.filter(q_object)

    def __filter_availability(self, products: QuerySet):
        index = self.get_index_by_qv('availability')
        if index is None:
            return products
        facet: Facet = self.facets[index]
        return_values = []
        for value in facet.values:
            count = products.filter_availability(value, self.location_pk).count()
            facet.total_count += count
            return_values.append(FacetValue(value, count, bool(facet.qterms and value in facet.qterms)))
        facet.return_values = return_values
        if facet.qterms:
            facet.selected = True
            products = products.filter_availability(facet.qterms, self.location_pk, True)
            return products
        return products

    def __get_mt_indices(self):
        mt_facets = self.get_indices_by_ft(MULTITEXT_FACET)
        kt_index = self.get_indices_by_ft(KEYTERM_FACET)
        color_index = self.get_indices_by_ft(COLOR_FACET)
        manu_index = self.get_indices_by_ft(MANUFACTURER_FACET)
        dep_index = self.get_indices_by_ft(DEPENDENT_FACET)
        indices = mt_facets + kt_index + color_index + manu_index + dep_index
        return indices

    def __filter_multi(self, products: QuerySet):
        indices = self.__get_mt_indices()
        for index in indices:
            facet = self.facets[index]
            if not facet.qterms:
                self.facets[index].queryset = products
                continue
            q_object = models.Q()
            for term in facet.qterms:
                q_object |= models.Q(**{facet.quer_value: term})
                facet.selected = True
            facet.queryset = products.filter(q_object)

    def __filter_location(self, products: QuerySet):
        loc_facet_index = self.get_indices_by_ft(LOCATION_FACET)
        if not loc_facet_index:
            return products
        loc_facet: Facet = self.facets[loc_facet_index[0]]
        self.facets[loc_facet_index[0]].return_values = [LocationFacet(value='location', default_radii=return_radii())]
        if not loc_facet.qterms:
            return products
        return_facet: LocationFacet = loc_facet.return_values[0]
        rad_raw = [q for q in loc_facet.qterms if 'radius' in q]
        zip_raw = [q for q in loc_facet.qterms if 'zip' in q]
        if not (rad_raw and zip_raw):
            return products
        radius_int = int(rad_raw[-1].replace('radius-', ''))
        return_facet.radius = radius_int
        radius = D(mi=radius_int)
        zipcode = zip_raw[-1].replace('zipcode-', '')
        coords = Zipcode.objects.filter(code=zipcode).first().centroid.point
        if not coords:
            return_facet.zipcode = 'invalid zipcode'
            return products
        return_facet.zipcode = zipcode
        return_facet.enabled = True
        new_products = products.filter(locations__distance_lte=(coords, radius))
        if not new_products:
            self.response.message = Message(note='Expand location for more results')
            self.response.return_products = False
            self.response.load_more = False
            return products
        loc_facet.return_values = [return_facet]
        loc_facet.selected = True
        return products

    def __range_iterator(self, products: QuerySet, index):
        facet = self.facets[index]
        _products, new_facet, contains_values = construct_range_facet(products, facet)
        if not contains_values:
            del self.facets[index]
            return _products
        self.facets[index] = new_facet
        return _products

    def __filter_range(self, products: QuerySet):
        _products = products
        range_indices = self.get_indices_by_ft(RANGE_FACET)
        if range_indices:
            for index in sorted(range_indices, reverse=True):
                _products = self.__range_iterator(_products, index)
            return _products
        price_indices = self.get_indices_by_ft(PRICE_FACET)
        if not price_indices:
            return _products
        if self.location_pk:
            sup_prods = products.retailer_products(self.location_pk)
            sup_prods = self.__range_iterator(sup_prods, price_indices[0])
            return self.product_type.objects.filter(pk__in=Subquery(sup_prods.values('product__pk')))
        return self.__range_iterator(_products, price_indices[0])

    def __filter_search_terms(self, products: QuerySet, search_term=None):
        if not search_term:
            return products
        searched_prods = products.annotate(
            search=SearchVector(
                'name',
                'manufacturer__label'
            )
        ).filter(search=search_term)
        if not searched_prods:
            self.response.return_products = False
            self.response.load_more = False
            self.response.message = Message(
                note='Test search produced no results. Make sure to use full words')
            return products
        return searched_prods

    def __get_counted_facet_indices(self):
        exclude_list = [RANGE_FACET, LOCATION_FACET, PRICE_FACET, AVAILABILITY_FACET]
        indices = []
        for count, _facet in enumerate(self.facets):
            if _facet.facet_type not in exclude_list:
                indices.append(count)
        return indices

    def __return_no_products(self):
        for index in self.__get_counted_facet_indices():
            facet = self.facets[index]
            if facet.values:
                facet.return_values = [
                    FacetValue(
                        value,
                        0,
                        bool(facet.qterms and value in facet.qterms)
                        ) for value in facet.values
                    ]
        self.response.message = 'No results'


@dataclass
class DetailListItem:
    name: str = None
    terms: List = None


@dataclass
class DetailResponse:
    unit: str = None
    manufacturer: str = None
    manufacturer_url: str = None
    swatch_image: str = None
    room_scene: str = None
    priced: List = None
    lists: List[DetailListItem] = None


class DetailBuilder:

    def __init__(self, pk: str):
        self.bb_sku = pk
        self.product = self.get_subclass_instance()
        self.response: DetailResponse = DetailResponse()

    def get_subclass_instance(self):
        product = Product.subclasses.filter(pk=self.bb_sku).select_subclasses().first()
        if not product:
            raise Exception('no product found for ' + self.bb_sku)
        return product

    def get_product_filter(self) -> ProductFilter:
        # model_type = type(self.get_subclass_instance())
        return get_filter(self.product)

    def get_priced(self):
        if self.product.get_in_store_priced():
            return list(RetailerProductMiniSerializer(self.product.get_in_store_priced(), many=True).data)
        return []

    def get_stock_details(self) -> DetailListItem:
        details_list = [{'term': attr[0], 'value': attr[1]} for attr in self.product.attribute_list() if attr[1]]
        return details_list

    def get_subclass_remaining(self):
        remaining_list = []
        model_fields = type(self.get_subclass_instance())._meta.get_fields(include_parents=False)
        model_fields = [field.name for field in model_fields if field.name != 'product_ptr']
        bool_attributes = self.get_bool_attributes()
        fields_to_check = [field for field in model_fields if field not in bool_attributes]
        for attr in fields_to_check:
            value = getattr(self.product, attr)
            if value:
                val_dict = {
                    'term': attr,
                    'value': value
                }
                remaining_list.append(val_dict)
        return remaining_list

    def get_bool_attributes(self):
        attributes = []
        filter_bools = self.get_product_filter().bool_groups
        for group in filter_bools:
            group_attrs = group.get('values', None)
            if group_attrs:
                attributes = attributes + group_attrs
        return attributes

    def get_bool_groups(self):
        filter_bools = self.get_product_filter().bool_groups
        groups_list = []
        for group in filter_bools:
            group_attrs = group.get('values', None)
            group_name = group.get('name', None)
            if group_attrs and group_name:
                group_vals = [{'term': attr, 'value': getattr(self.product, attr)} for attr in group_attrs]
                groups_list.append(DetailListItem(group_name, group_vals))
        return groups_list

    def assign_response(self):
        self.response.lists = self.get_bool_groups()
        details_list = self.get_stock_details() + self.get_subclass_remaining()
        self.response.lists.append(DetailListItem('details', details_list))
        self.response.priced = self.get_priced()
        self.response.manufacturer = self.product.manufacturer_name()
        self.response.manufacturer_url = self.product.manufacturer_url
        self.response.swatch_image = self.product.swatch_image.url if self.product.swatch_image else None
        self.response.room_scene = self.product.room_scene.url if self.product.room_scene else None
        self.response.unit = self.product.unit

    def assign_detail_response(self):
        self.assign_response()
        detail_dict = asdict(self.response)
        product: Product = Product.objects.filter(pk=self.bb_sku).first()
        product.detail_response = detail_dict
        product.save()
        return product.detail_response

    def get_reponse(self, update=False):
        detail_response = self.product.detail_response
        if detail_response and not update:
            return detail_response
        return self.assign_detail_response()


    # may need to use structure below:
    # if field_type in acceptable_fields[:2]:
    #     values = self.get_model_products().aggregate(Min(Lower(standalone)), Max(Upper(standalone)))
    # else:
    #     values = self.get_model_products().aggregate(Min(standalone), Max(standalone))
