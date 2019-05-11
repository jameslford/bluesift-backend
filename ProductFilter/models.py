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
        self.facets.append(Facet('Price', 'PriceFacet', 'DecimalField', list(price_values)))
        self.facets.append(Facet('Availability', 'AvailabilityFacet', 'BooleanField', ['for_sale_in_store']))
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


class Sorter:
    """ takes a request and returns a filter and product set """
    def __init__(self, product_filter: ProductFilter, request: HttpRequest, update=False):
        self.product_filter = product_filter
        self.query_index: QueryIndex = None
        self.request = request
        self.search_term = None
        self.page = None
        self.ordering_term = None
        self.facets = []
        self.response = {
            'legit_queries': [],
            'message': None,
            'filter': None,
            'products': None
        }
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
        self.page = int(self.request.GET.get('page', 1))
        self.search_term = self.request.GET.get('search', None)
        self.ordering_term = self.request.GET.get('order_term', None)
        for facet in self.product_filter.facets:
            queries = query.split('&')
            applicable = [q.replace(f'{facet.quer_value}-', '') for q in queries if facet.quer_value in q]
            facet['qterms'] = applicable
            self.facets.append(facet)
        self.__filter_products()

    def __filter_products(self):
        products = self.product_filter.get_model_products()
        products = self.__filter_search_terms(products)
        products = self.__filter_location(products)


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
            self.response['message'] = 'No results'
            return []
        return searched_prods

    def get_index(self, keyword: str):
        for count, facet in enumerate(self.facets):
            if facet['quer_value'] == keyword:
                return count
        raise Exception(keyword + ' not found in facets')

    def __filter_location(self, products: QuerySet):
        loc_facet = self.facets[self.get_index('location')]
        rad_raw = [q for q in loc_facet['qterms'] if 'radius' in q]
        zip_raw = [q for q in loc_facet['qterms'] if 'zip' in q]
        if not (rad_raw and zip_raw):
            return products
        radius_int = int(rad_raw[-1].replace('radius-', ''))
        loc_facet['values'].append({'selected_radius': radius_int})
        radius = D(mi=radius_int)
        zipcode = zip_raw[-1].replace('zipcode-', '')
        coords = Zipcode.objects.filter(code=zipcode).first().centroid.point
        if not coords:
            loc_facet['values'].append({'zipcode': 'invalid zipcode'})
            return products
        loc_facet['vales'].append({'zipcode': int(zipcode)})
        # finish this
        return products
