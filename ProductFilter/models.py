import json
from decimal import Decimal
from dataclasses import dataclass, asdict
from dataclasses import field as dfield
from typing import List, Tuple
from django.db import models
from django.db.models.functions import Upper, Lower
from django.db.models import Min, Max
from django.contrib.postgres.search import SearchVector
from django.contrib.gis.measure import D
from django.db.models.query import QuerySet
from django.http import HttpRequest, QueryDict
from django.core import exceptions
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields
from config.scripts.globals import PRODUCT_SUBCLASSES
from Addresses.models import Zipcode
from Products.serializers import SerpyProduct
from Products.models import Product
from Profiles.serializers import SupplierProductMiniSerializer


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

def subclass_content_types():
    ct_choices = []
    for name, subclass in PRODUCT_SUBCLASSES.items():
        ct = ContentType.objects.get_for_model(subclass)
        kwargs = {'app_label': ct.app_label, 'model': ct.model}
        ct_choices.append(models.Q(**kwargs))
    query = ct_choices.pop()
    for ct_choice in ct_choices:
        query |= ct_choice
    return query


@dataclass
class FacetValue:
    """ datastructure for facet value
        FacetValue(value: str, count: int, enabled: bool)
    """
    value: str
    count: int = None
    enabled: bool = False


@dataclass
class Facet:
    """ data structure for filter
        Facet(name: str, facet_type: str, quer_value, values: [str])
     """
    name: str
    facet_type: str
    quer_value: str
    values: List = None
    total_count: int = 0
    qterms: List[str] = None
    queryset: QuerySet = None
    return_values: List[FacetValue] = dfield(default_factory=lambda: [])


class QueryIndex(models.Model):
    """ cache relating query strings to json responses"""
    query_string = models.CharField(max_length=1000)
    response = pg_fields.JSONField(null=True)
    product_filter = models.ForeignKey(
        'ProductFilter',
        on_delete=models.CASCADE,
        related_name='query_indexes'
    )
    created = models.DateTimeField(auto_now=True)
    last_retrieved = models.DateTimeField(null=True)
    times_accessed = models.PositiveIntegerField(null=True, default=1)

    class Meta:
        unique_together = ('query_string', 'product_filter')


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
        limit_choices_to=subclass_content_types(),
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
        try:
            field = mymodel._meta.get_field(name)
            field_type = field.get_internal_type()
            if fieldnames and field_type not in fieldnames:
                return [False, field_type]
            return [True, field_type]
        except exceptions.FieldDoesNotExist:
            return [False, None]

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
            valid_groups.append(Facet(group['name'], BOOLGROUP_FACET, group['name'], valid_values))
        self.facets = self.facets + valid_groups

    def check_keyterm(self):
        check = self.check_value(self.key_field)
        if not check:
            self.key_field = None
            return
        products = self.get_model_products().values_list(self.key_field, flat=True).distinct()
        self.facets.append(Facet(self.key_field, KEYTERM_FACET, self.key_field, list(products)))

    def check_mc_fields(self):
        indices = sorted(enumerate(self.independent_multichoice_fields), reverse=True)
        for count, standalone in indices:
            check = self.check_value(standalone)[0]
            if not check:
                del self.independent_multichoice_fields[count]
                continue
            products = self.get_model_products().values_list(standalone, flat=True).distinct()
            self.facets.append(Facet(standalone, MULTITEXT_FACET, standalone, list(products)))

    def check_range_fields(self):
        range_fields = [pg_fields.IntegerRangeField, pg_fields.DecimalRangeField]
        discreet_fields = [models.DecimalField, models.IntegerField]
        acceptable_fields = [f.__name__ for f in range_fields + discreet_fields]
        for count, standalone in sorted(enumerate(self.independent_range_fields), reverse=True):
            check, field_type = self.check_value(standalone, acceptable_fields)
            if not check:
                del self.independent_range_fields[count]
                continue
            values = self.get_model_products().aggregate(Min(standalone), Max(standalone))
            self.facets.append(Facet(standalone, RANGE_FACET, standalone, list(values)))

            # may need to use structure below:
            # if field_type in acceptable_fields[:2]:
            #     values = self.get_model_products().aggregate(Min(Lower(standalone)), Max(Upper(standalone)))
            # else:
            #     values = self.get_model_products().aggregate(Min(standalone), Max(standalone))

    def check_color_field(self):
        check, fieldtype = self.check_value(self.color_field)
        if not check:
            self.color_field = None
            return
        values = self.get_model_products().values_list(self.color_field, flat=True).distinct()
        self.facets.append(Facet('color', COLOR_FACET, self.color_field, list(values)))

    def check_dependents(self):
        for count, dependent in sorted(enumerate(self.dependent_fields), reverse=True):
            if not self.check_value(dependent):
                del self.dependent_fields[count]
            values = self.get_model_products().values_list(dependent, flat=True).distinct()
            self.facets.append(Facet(dependent, DEPENDENT_FACET, dependent, list(values)))

    def add_product_facets(self):
        price_values = self.get_model_products().aggregate(Min('lowest_price'), Max('lowest_price'))
        self.facets.append(Facet('price', PRICE_FACET, 'lowest_price', list(price_values)))
        self.facets.append(Facet('availability', AVAILABILITY_FACET, 'availability', ['for_sale_in_store']))
        manu_values = self.get_model_products().values_list('manufacturer__label', flat=True).distinct()
        self.facets.append(Facet('manufacturer', MANUFACTURER_FACET, 'manufacturer__label', list(manu_values)))
        self.facets.append(Facet('location', LOCATION_FACET, 'location', [{'default_radii': [5, 10, 15, 25, 50, 100]}]))

    def check_fields(self):
        self.add_product_facets()
        self.check_bools()
        self.check_keyterm()
        self.check_color_field()
        self.check_mc_fields()
        self.check_dependents()

    def add_filter_dictionary(self):
        self.filter_dictionary = [asdict(facet) for facet in self.facets]

    def refresh_QueryIndex(self):
        """ refreshes all QueryIndex objects that are linked to self
        """
        existing_queries = self.query_indexes.values_list('query_string', flat=True).distinct()
        for query in existing_queries:
            Sorter(self.get_content_model(), querystring=query)

    def save(self, *args, **kwargs):
        self.filter_dictionary = None
        self.check_fields()
        self.add_filter_dictionary()
        self.refresh_QueryIndex()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_content_model().__name__ + ' Filter'


@dataclass
class FilterResponse:
    legit_queries: List[str] = dfield(default_factory=list)
    page: int = 1
    load_more: bool = True
    message: str = None
    product_count: int = 0
    filter_dict: List[dict] = None
    products: List[dict] = None


class Sorter:
    """ takes a request and returns a filter and product set """
    def __init__(self, product_subclass: models.Model, request: HttpRequest = None, update=False, querystring: str = None,):
        self.product_filter = self.get_filter(product_subclass)
        self.query_index: QueryIndex = None
        self.search_term = None
        self.availabity = False
        self.page_size = 60
        self.qi_response = None
        self.ordering_term = None
        self.facets: List[Facet] = []
        self.response: FilterResponse = FilterResponse()
        self.__route_operation(request, querystring, update)

    def __route_operation(self, request: HttpRequest = None, querystring: str = None, update=False):
        if request and querystring:
            raise Exception('Cannot pass request and querystring')
        if request:
            self.__parse_request(request, update)
        if querystring:
            self.__parse_querystring(querystring)

    def __parse_request(self, request: HttpRequest, update: bool):
        if request.method != 'GET':
            self.response.message = 'Invalid request method'
            return
        self.__process(request.GET, update)

    def __parse_querystring(self, querystring: str):
        self.__process(QueryDict(querystring), True)

    def get_content_type(self, model: models.Model) -> ContentType:
        content_type = ContentType.objects.get_for_model(model)
        return content_type

    def get_filter(self, model: models.Model) -> ProductFilter:
        content_type = self.get_content_type(model)
        prod_filter = ProductFilter.objects.filter(sub_product=content_type).first()
        if not prod_filter:
            raise Exception('No filter for this class')
        return prod_filter

    def __process(self, request_dict: QueryDict, update=False):
        query_params = request_dict.urlencode()
        query_index, created = QueryIndex.objects.get_or_create(
            query_string=query_params,
            product_filter=self.product_filter
            )
        if not created and not update:
            query_index.times_accessed += 1
            query_index.last_accessed = now()
            query_index.save()
            self.qi_response = query_index.response
            return
        self.query_index = query_index
        self.__parse_querydict(request_dict)

    def __parse_querydict(self, request_dict: QueryDict):
        self.response.page = int(request_dict.get('page', 1))
        self.search_term = request_dict.get('search', None)
        self.ordering_term = request_dict.get('order_term', None)
        for f_dict in self.product_filter.filter_dictionary:
            facet = Facet(**f_dict)
            facet.qterms = request_dict.getlist(facet.quer_value, None)
            self.facets.append(facet)
        self.__build_response()

    def __build_response(self):
        self.__check_availability_facet()
        products = self.product_filter.get_model_products()
        products = self.__filter_search_terms(products)
        products = self.__filter_location(products)
        products = self.__filter_price(products)
        products = self.__filter_range(products)
        self.__filter_bools(products.all())
        self.__filter_multi(products.all())
        self.__count_objects(products)
        self.__assign_response_to_QI()

    def __filter_search_terms(self, products: QuerySet):
        if not self.search_term:
            return products
        searched_prods = products.annotate(
            search=SearchVector(
                'name',
                'manufacturer__label'
            )
        ).filter(search=self.search_term)
        if not searched_prods:
            self.response.message = 'No results'
            return []
        return searched_prods

    def get_index_by_qv(self, keyword: str):
        for count, facet in enumerate(self.facets):
            facet: Facet = facet
            if facet.quer_value == keyword:
                return count
        raise Exception(keyword + ' not found in facets')

    def get_indices_by_ft(self, facet_type: str) -> [int]:
        indices = []
        for count, facet in enumerate(self.facets):
            if facet.facet_type == facet_type:
                indices.append(count)
        return indices

    def __check_availability_facet(self):
        avail_facet: Facet = self.facets[self.get_index_by_qv('availability')]
        q_terms = avail_facet.qterms
        values = avail_facet.values
        for q_term in q_terms:
            if q_term in values:
                self.availabity = True
                self.response.legit_queries.append(f'availability-{q_term}')
            else:
                avail_facet.qterms.remove(q_term)

    def __filter_location(self, products: QuerySet):
        loc_facet_index = self.get_index_by_qv('location')
        if not self.availabity:
            del self.facets[loc_facet_index]
            return products
        loc_facet: Facet = self.facets[loc_facet_index]
        rad_raw = [q for q in loc_facet.qterms if 'radius' in q]
        zip_raw = [q for q in loc_facet.qterms if 'zip' in q]
        if not (rad_raw and zip_raw):
            return products
        radius_int = int(rad_raw[-1].replace('radius-', ''))
        loc_facet.values.append({'selected_radius': radius_int})
        radius = D(mi=radius_int)
        zipcode = zip_raw[-1].replace('zipcode-', '')
        coords = Zipcode.objects.filter(code=zipcode).first().centroid.point
        if not coords:
            loc_facet['values'].append({'zipcode': 'invalid zipcode'})
            return products
        loc_facet['values'].append({'zipcode': int(zipcode)})
        self.response.legit_queries = [
            'location-radius-' + radius_int,
            'location-zipcode-' + zipcode
            ]
        new_products = products.filter(locations__distance_lte=(coords, radius))
        if not new_products:
            self.response.message = 'No results'
            return None
        return products

    def __filter_price(self, products: QuerySet):
        price_facet_index = self.get_index_by_qv('lowest_price')
        if not self.availabity:
            del self.facets[price_facet_index]
            return products
        return self.__filter_range(products, price_facet_index)

    def __filter_range(self, products: QuerySet, facet_index=None):
        facet_indicies = [self.facets[facet_index]] if facet_index else self.get_indices_by_ft(RANGE_FACET)
        if not facet_indicies:
            return products
        for index in facet_indicies:
            facet = self.facets[index]
            if not facet.qterms:
                facet.queryset = products
                continue
            min_query = [q.replace('min-', '') for q in facet.q_terms if 'min' in q]
            max_query = [q.replace('max-', '') for q in facet.q_terms if 'max' in q]
            if min_query:
                products = self.__complete_range(products, facet, min_query, 'min')
            if max_query:
                products = self.__complete_range(products, facet, max_query, 'max')
            if not products:
                self.response.message = 'No results'
                return None
        return products

    def __complete_range(self, products: QuerySet, facet, query, direction: str):
        qrange = Decimal(query[-1])
        direction_transform = {'min': 'gte', 'max': 'lte'}
        quer_value = facet.quer_value
        self.response.legit_queries.append(f'{quer_value}-{direction}-{str(qrange)}')
        facet.values.append({f'{direction}-range': qrange})
        argument = {f'{quer_value}__{direction_transform[direction]}': qrange}
        return products.filter(**argument)

    def __filter_bools(self, products: QuerySet):
        bool_indices = self.get_indices_by_ft(BOOLGROUP_FACET)
        bool_indices.append(self.get_index_by_qv('availability'))
        legit_queries = []
        for index in bool_indices:
            search_terms = {}
            facet = self.facets[index]
            if not facet.qterms:
                self.facets[index].queryset = products
                continue
            for term in facet.qterms:
                search_terms[term] = True
                legit_queries.append(f'{facet.quer_value}-{term}')
            facet.queryset = products.filter(**search_terms)
        self.response.legit_queries = self.response.legit_queries + legit_queries

    def __check_keyterm(self):
        indices = self.get_indices_by_ft(MULTITEXT_FACET)
        kt_index = self.get_indices_by_ft(KEYTERM_FACET)
        color_index = self.get_indices_by_ft(COLOR_FACET)
        manu_index = self.get_indices_by_ft(MANUFACTURER_FACET)
        indices = indices + kt_index + color_index + manu_index
        if not kt_index:
            self.__delete_dependents()
            return indices
        keyterm_facet = self.facets[kt_index[0]]
        if not keyterm_facet.qterms:
            self.__delete_dependents()
            return indices
        indices = indices + self.get_indices_by_ft(DEPENDENT_FACET)
        return indices

    def __delete_dependents(self):
        facet_indices = self.get_indices_by_ft(DEPENDENT_FACET)
        for index in sorted(facet_indices, reverse=True):
            del self.facets[index]

    def __filter_multi(self, products: QuerySet):
        indices = self.__check_keyterm()
        legit_queries = []
        for index in indices:
            facet = self.facets[index]
            if not facet.qterms:
                self.facets[index].queryset = products
                continue
            q_object = models.Q()
            for term in facet.qterms:
                q_object |= models.Q(**{facet.quer_value: term})
                legit_queries.append(f'{facet.quer_value}-{term}')
            facet.queryset = products.filter(q_object)
        self.response.legit_queries = self.response.legit_queries + legit_queries

    def __get_counted_facet_indices(self):
        exclude_list = [RANGE_FACET, LOCATION_FACET, PRICE_FACET]
        indices = []
        for count, _facet in enumerate(self.facets):
            if _facet.facet_type not in exclude_list:
                indices.append(count)
        return indices

    def __count_objects(self, products: QuerySet):
        all_qs = []
        indices = self.__get_counted_facet_indices()
        for index in indices:
            facet = self.facets[index]
            if not facet.queryset:
                self.__return_no_products()
                return
            _products = products.all()
            others = [o for o in indices if o != index]
            q_sets = [self.facets[q].queryset for q in others]
            all_qs.append(facet.queryset)
            return_values = []
            for value in facet.values:
                term = {facet.quer_value: value}
                if facet.facet_type in (BOOLGROUP_FACET, AVAILABILITY_FACET):
                    term = {value: True}
                count = _products.filter(**term).intersection(*q_sets).count()
                facet.total_count += count
                return_values.append(FacetValue(
                    value,
                    count,
                    bool(value in facet.qterms)
                ))
            facet.return_values = return_values
        self.__set_filter_dict()
        final_qs = products.all().intersection(*all_qs)
        self.response.product_count = final_qs.count()
        self.__serialize_products(final_qs)

    def __return_no_products(self):
        for index in self.__get_counted_facet_indices():
            facet = self.facets[index]
            return_values = []
            for value in facet.values:
                return_values.append(FacetValue(
                    value,
                    0,
                    bool(value in facet.qterms)
                ))
            facet.return_values = return_values
        self.response.message = 'No results'
        self.__set_filter_dict()

    def __set_filter_dict(self):
        indices = self.__get_counted_facet_indices()
        for index in indices:
            self.facets[index].queryset = None
            self.facets[index].values = None
        self.response.filter_dict = [asdict(qfacet) for qfacet in self.facets]

    def __serialize_products(self, products: QuerySet):
        start_page = self.response.page - 1
        product_start = start_page * self.page_size
        product_end = self.response.page * self.page_size
        if product_end > self.response.product_count:
            self.response.load_more = False
            _products = products[product_start:]
        _products = products[product_start:product_end]
        self.response.products = SerpyProduct(_products, many=True).data

    def __assign_response_to_QI(self):
        self.query_index.response = asdict(self.response)
        self.query_index.save()

    def get_repsonse(self):
        """ retrieves repsonse dictionary, built by sorter

        Returns:
            dictionary -- if self instantiate by a request, will return a response dictionary for associated queryindex
            if the query has been retrieved before. Else, it will build a new dictionary, which has been associated to the qi
        """
        if self.qi_response:
            return self.qi_response
        return asdict(self.response)


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
        product = Product.objects.filter(pk=self.bb_sku).select_subclasses().first()
        if not product:
            raise Exception('no product found for ' + self.bb_sku)
        return product

    def get_product_filter(self) -> ProductFilter:
        model_type = type(self.get_subclass_instance())
        return Sorter(model_type).product_filter

    def get_priced(self):
        if self.product.in_store_priced():
            return SupplierProductMiniSerializer(self.product.in_store_priced(), many=True).data
        return []

    def get_stock_details(self) -> DetailListItem:
        details_list = [{'term': attr[0], 'values': attr[1]} for attr in self.product.attribute_list() if attr[1]]
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
        self.response.lists = [self.get_bool_groups()]
        details_list = self.get_stock_details() + self.get_subclass_remaining()
        self.response.lists.append(DetailListItem('details', details_list))
        self.response.priced = self.get_priced()
        self.response.manufacturer = self.product.manufacturer_name()
        self.response.manufacturer_url = self.product.manufacturer_url
        self.response.swatch_image = self.product.swatch_image.url
        self.response.room_scene = self.product.room_scene.url if self.product.room_scene else None
        self.response.unit = self.product.unit

    def assign_detail_response(self):
        self.assign_response()
        detail_dict = asdict(self.response)
        product: Product = Product.objects.filter(pk=self.bb_sku).first()
        product.detail_response = detail_dict
        product.save()
        return product.detail_response

    def get_reponse(self):
        detail_response = self.product.detail_response
        if detail_response:
            return detail_response
        return self.assign_detail_response()
