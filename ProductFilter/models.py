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
from Products.serializers import SubClassSerializer

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

    facets = []
    content_model = None
    products: QuerySet = None
    sub_product = models.OneToOneField(
        ContentType,
        limit_choices_to=subclass_content_types(),
        on_delete=models.CASCADE
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
        if not self.content_model:
            self.content_model = self.sub_product.model_class()
        return self.content_model

    def get_model_products(self):
        if not self.products:
            model = self.get_content_model()
            self.products = model.objects.all()
        return self.products

    def check_value(self, name, fieldname: List[str] = None) -> Tuple[bool, str]:
        mymodel = self.get_content_model()
        try:
            field = mymodel._meta.get_field(name)
            field_type = field.get_internal_type()
            if fieldname and field_type not in fieldname:
                return [False, field_type]
            return [True, field_type]
        except exceptions.FieldDoesNotExist:
            return [False, None]

    def check_bools(self):
        if not self.bool_groups:
            return
        valid_groups = []
        for group_count, group in enumerate(self.bool_groups):
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
            valid_groups.append(Facet(group['name'], 'BoolGroupFacet', group['name'], valid_values))
        self.facets = self.facets + valid_groups

    def check_keyterm(self):
        check, field_type = self.check_value(self.key_field)
        if not check:
            self.key_field = None
            return
        products = self.get_model_products().values_list(self.key_field, flat=True).distinct()
        self.facets.append(Facet(self.key_field, 'KeyTermFacet', self.key_field, list(products)))

    def check_mc_fields(self):
        for count, standalone in enumerate(self.independent_multichoice_fields):
            check, field_type = self.check_value(standalone)
            if not check:
                del self.independent_multichoice_fields[count]
                continue
            products = self.get_model_products().values_list(standalone, flat=True).distinct()
            self.facets.append(Facet(standalone, 'MultiTextFacet', standalone, list(products)))

    def check_range_fields(self):
        range_fields = [pg_fields.IntegerRangeField, pg_fields.DecimalRangeField]
        discreet_fields = [models.DecimalField, models.IntegerField]
        acceptable_fields = [f.__name__ for f in range_fields + discreet_fields]
        for count, standalone in enumerate(self.independent_range_fields):
            check, field_type = self.check_value(standalone, acceptable_fields)
            if not check:
                del self.independent_range_fields[count]
                continue
            values = self.get_model_products().aggregate(Min(standalone), Max(standalone))
            self.facets.append(Facet(standalone, 'RangeFacet', standalone, list(values)))

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
        self.facets.append(Facet('color', 'ColorFacet', self.color_field, list(values)))

    def check_dependents(self):
        for count, dependent in enumerate(self.dependent_fields):
            if not self.check_value(dependent):
                del self.dependent_fields[count]
            values = self.get_model_products().values_list(dependent, flat=True).distinct()
            self.facets.append(Facet(dependent, 'DependentFacet', dependent, list(values)))

    def add_product_facets(self):
        price_values = self.get_model_products().aggregate(Min('lowest_price'), Max('lowest_price'))
        self.facets.append(Facet('price', 'PriceFacet', 'lowest_price', list(price_values)))
        self.facets.append(Facet('availability', 'AvailabilityFacet', 'availability', ['for_sale_in_store']))
        manu_values = self.get_model_products().values_list('manufacturer__label', flat=True).distinct()
        # manu_values = [q for q in manu_values]
        print(list(manu_values))
        self.facets.append(Facet('manufacturer', 'ManufacturerFacet', 'manufacturer__label', list(manu_values)))
        self.facets.append(Facet('location', 'LocationFacet', 'location', [{'default_radii': [5, 10, 15, 25, 50, 100]}]))

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
        existing_queries = self.query_indexes.values_list('query_string', flat=True).distinct()
        for query in existing_queries:
            print('qs = ' + query)
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
        query = request_dict.getlist('quer', None)
        self.response.page = int(request_dict.get('page', 1))
        self.search_term = request_dict.get('search', None)
        self.ordering_term = request_dict.get('order_term', None)
        for f_dict in self.product_filter.filter_dictionary:
            facet = Facet(**f_dict)
            queries = [q.strip('&') for q in query]
            applicable = [q.replace(f'{facet.quer_value}-', '') for q in queries if facet.quer_value in q]
            facet.qterms = applicable
            self.facets.append(facet)
            print(facet)
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
        products = self.__count_objects(products)
        self.__serialize_products(products)
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
        loc_facet: Facet = self.facets[loc_facet_index]
        if not self.availabity:
            # self.facets.remove(loc_facet)
            # del self.facets[loc_facet_index]
            # self.facets = [f for f in self.facets if f]
            return products
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
            # del self.facets[price_facet_index]
            return products
        return self.__filter_range(products, price_facet_index)

    def __filter_range(self, products: QuerySet, facet_index=None):
        facet_indicies = [self.facets[facet_index]] if facet_index else self.get_indices_by_ft('RangeFacet')
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
        bool_indices = self.get_indices_by_ft('BoolGroupFacet')
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
        indices = self.get_indices_by_ft('MultiTextFacet')
        kt_index = self.get_indices_by_ft('KeyTermFacet')
        color_index = self.get_indices_by_ft('ColorFacet')
        manu_index = self.get_indices_by_ft('ManufacturerFacet')
        indices = indices + kt_index + color_index + manu_index
        if not kt_index:
            self.__delete_dependents()
            return indices
        keyterm_facet = self.facets[kt_index[0]]
        if not keyterm_facet.qterms:
            self.__delete_dependents()
            return indices
        indices = indices + self.get_indices_by_ft('DependentFacet')
        return indices

    def __delete_dependents(self):
        facet_indices = self.get_indices_by_ft('DependentFacet')
        for index in facet_indices:
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

    def __count_objects(self, products: QuerySet):
        exclude_list = ['RangeFacet', 'LocationFacet', 'PriceFacet']
        indices = []
        all_qs = []
        for count, _facet in enumerate(self.facets):
            if _facet.facet_type not in exclude_list:
                indices.append(count)
        for index in indices:
            _products = products.all()
            others = [o for o in indices if o != index]
            q_sets = [self.facets[q].queryset for q in others]
            q_sets = [q for q in q_sets if q]
            facet = self.facets[index]
            if facet.queryset:
                all_qs.append(facet.queryset)
            else:
                print('no queryset for ' + facet.name)
            return_values = []
            for value in facet.values:
                term = {facet.quer_value: value}
                if facet.facet_type in ('BoolGroupFacet', 'AvailabilityFacet'):
                    term = {value: True}
                count = _products.filter(**term).intersection(*q_sets).count()
                facet.total_count += count
                return_values.append(FacetValue(
                    value,
                    count,
                    bool(value in facet.qterms)
                ))
            facet.return_values = return_values
        for index in indices:
            facet = self.facets[index]
            facet.queryset = None
            facet.values = None
        self.response.filter_dict = [asdict(qfacet) for qfacet in self.facets]
        final_qs = products.all().intersection(*all_qs)
        self.response.product_count = final_qs.count()
        return final_qs

    def __serialize_products(self, products: QuerySet):
        start_page = self.response.page - 1
        product_start = start_page * self.page_size
        product_end = self.response.page * self.page_size
        if product_end > self.response.product_count:
            self.response.load_more = False
            _products = products[product_start:]
        _products = products[product_start:product_end]
        self.response.products = SubClassSerializer(_products, many=True).data

    def __assign_response_to_QI(self):
        self.query_index.response = asdict(self.response)
        self.query_index.save()

    def get_repsonse(self):
        if self.qi_response:
            return self.qi_response
        return asdict(self.response)
