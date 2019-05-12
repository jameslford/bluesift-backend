from decimal import Decimal
from dataclasses import dataclass, asdict
from typing import List, Tuple
from django.db import models
from django.db.models.functions import Upper, Lower
from django.db.models import Min, Max
from django.contrib.postgres.search import SearchVector
from django.contrib.gis.measure import D
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.core import exceptions
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields
from config.scripts.globals import PRODUCT_SUBCLASSES
from Addresses.models import Zipcode


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
class Facet:
    """ data structure for filter
        Facet(name: str, facet_type: str, quer_value, values: [str])
     """
    name: str
    facet_type: str
    quer_value: str
    values: List[str] = None
    total_count: int = 0
    qterms: List[str] = None


class QueryIndex(models.Model):
    """ cache relating query strings to json responses"""
    query_string = models.CharField(max_length=1000)
    response = pg_fields.JSONField()
    product_filter = models.ForeignKey(
        'ProductFilter',
        on_delete=models.CASCADE,
        related_name='query_indexes'
    )
    created = models.DateTimeField(auto_now=True)
    last_retrieved = models.DateTimeField()
    times_accessed = models.PositiveIntegerField()

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
            for key in group.keys():
                if key != ('values' or 'name'):
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
        values = self.get_model_products().values_list('label_color', flat=True).distinct()
        self.facets.append(Facet('color', 'ColorFacet', 'label_color', list(values)))

    def check_dependents(self):
        for count, dependent in enumerate(self.dependent_fields):
            if not self.check_value(dependent):
                del self.dependent_fields[count]

    def add_product_facets(self):
        price_values = self.get_model_products().aggregate(Min('lowest_price'), Max('lowest_price'))
        self.facets.append(Facet('price', 'PriceFacet', 'lowest_price', list(price_values)))
        self.facets.append(Facet('availability', 'AvailabilityFacet', 'availability', ['for_sale_in_store']))
        manu_values = self.get_model_products().values_list('manufacturer__label').distinct()
        self.facets.append(Facet('manufacturer', 'ManufacturerFacet', 'manufacuter__label', list(manu_values)))
        self.facets.append(Facet('location', 'LocationFacet', 'location', [{'default_radii': [5, 10, 15, 25, 50, 100]}]))

    def check_fields(self):
        self.add_product_facets()
        self.check_bools()
        self.check_keyterm()
        self.check_mc_fields()
        self.check_dependents()

    def add_filter_dictionary(self):
        self.filter_dictionary = [asdict(facet) for facet in self.facets]


    def save(self, *args, **kwargs):
        self.check_fields()
        self.add_filter_dictionary()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_content_model().__name__ + ' Filter'


@dataclass
class FilterResponse:
    legit_queries: str = None
    page: int = 1
    message: str = None
    filter_dict: List[dict] = None
    products: List[dict] = None


class Sorter:
    """ takes a request and returns a filter and product set """
    def __init__(self, product_filter: ProductFilter, request: HttpRequest, update=False):
        self.product_filter = product_filter
        self.query_index: QueryIndex = None
        self.request = request
        self.search_term = None
        self.availabity = False
        self.ordering_term = None
        self.facets: List[Facet] = []
        self.response: FilterResponse = FilterResponse()
        self.__get_response(update)

    def __get_response(self, update=False):
        if self.request.method != 'GET':
            self.response['message'] = 'Invalid request method'
            return
        query_params = self.request.GET.urlencode()
        query_index, created = QueryIndex.objects.get_or_create(
            query_string=query_params,
            product_filter=self.product_filter
            )
        if not created and not update:
            query_index.times_accessed += 1
            query_index.last_accessed = now()
            query_index.save()
            self.response = query_index.response
            return
        self.query_index = query_index
        self.__parse_request()

    def __parse_request(self):
        query = self.request.GET.getlist('quer', None)
        self.response.page = int(self.request.GET.get('page', 1))
        self.search_term = self.request.GET.get('search', None)
        self.ordering_term = self.request.GET.get('order_term', None)
        for facet in self.product_filter.facets:
            queries = query.split('&')
            applicable = [q.replace(f'{facet.quer_value}-', '') for q in queries if facet.quer_value in q]
            facet.qterms = applicable
            self.facets.append(facet)
        self.__filter_products()

    def __filter_products(self):
        self.__check_availability_facet()
        products = self.product_filter.get_model_products()
        products = self.__filter_search_terms(products)
        products = self.__filter_location(products)
        products = self.__filter_price(products)
        products = self.__filter_range(products)

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
            facet: Facet = facet
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
        loc_facet: Facet = self.facets[self.get_index_by_qv('location')]
        if not self.availabity:
            self.facets.remove(loc_facet)
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
        price_facet_index = self.get_index_by_qv('price')
        if not self.availabity:
            del self.facets[price_facet_index]
            return products
        return self.__filter_range(products, price_facet_index)

    def __filter_range(self, products: QuerySet, facet_index=None):
        facet_indicies = [self.facets[facet_index]] if facet_index else self.get_indices_by_ft('RangeFacet')
        if not facet_indicies:
            return products
        _products = products
        for index in facet_indicies:
            facet = self.facets[index]
            q_terms = facet.qterms
            min_query = [q.replace('min-', '') for q in q_terms if 'min' in q]
            max_query = [q.replace('max-', '') for q in q_terms if 'max' in q]
            if min_query:
                _products = self.__complete_range(_products, facet, min_query, 'min')
            if max_query:
                _products = self.__complete_range(_products, facet, max_query, 'max')
            if not _products:
                self.response.message = 'No results'
                return None
        return _products

    def __complete_range(self, products: QuerySet, facet, query, direction: str):
        qrange = Decimal(query[-1])
        direction_transform = {'min': 'gte', 'max': 'lte'}
        quer_value = facet.quer_value
        self.response['legit_queries'].append(f'{quer_value}-{direction}-{str(qrange)}')
        facet.values.append({f'{direction}-range': qrange})
        argument = {f'{quer_value}__{direction_transform[direction]}': qrange}
        return products.filter(**argument)

    def __filter_bools(self, products: QuerySet):
        bool_indices = self.get_indices_by_ft('BoolGroupFacet')
        bool_indices.append(self.get_index_by_qv('availability'))
        legit_queries = []
        search_terms = {}
        for index in bool_indices:
            facet = self.facets[index]
            qterms = facet.qterms
            for term in qterms:
                search_terms[term] = True
                legit_queries.append(f'{facet.quer_value}-{term}')
        self.response.legit_queries = self.response.legit_queries + legit_queries
        return products.filter(**search_terms)

    def __filter_multi(self):
        
        pass

    def __filter_manufacturer(self):
        pass

    def __order(self):
        pass

    def __paginate(self):
        pass
