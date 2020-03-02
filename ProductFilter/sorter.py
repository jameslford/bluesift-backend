import itertools
import pickle
from typing import List
from rest_framework.request import Request
from django.core.files.storage import get_storage_class
from django.core.cache import cache
from django.db.models.functions import Concat
from django.http import QueryDict
from django.db.models.query import QuerySet, Value
from django.db.models import CharField
from django.db import transaction
from Suppliers.models import SupplierProduct
from Products.models import Product
from .models import (
    load_facets,
    BaseFacet,
    QueryIndex,
    )





class FilterResponse:
    def __init__(self, product_count: int, facets: List[BaseFacet], products: QuerySet, enabled_values):
        self.product_count = product_count
        self.facets = [facet for facet in facets if facet]
        self.products = products
        self.enabled_values = enabled_values


    def set_cache(self, path_key):
        facets = [facet.serialize_self() for facet in self.facets]
        pickle_dict = {
            'product_count': self.product_count,
            'facets': [facet for facet in facets if facet],
            'enabled_values': self.enabled_values,
            'products': list(self.serialize_products(self.products))
            }
        cache.set(path_key, pickle_dict, 60 * 10)


    @classmethod
    def get_cache(cls, path, start, end):
        res_dict = cache.get(path)
        if not res_dict:
            return None
        prods = res_dict.get('products')
        res_dict['products'] = prods[start: end]
        return res_dict

    def serialize_cached(self, product_count, facets, enabled_values, products, start, end):
        return {
            'product_count': product_count,
            'facets': facets,
            'enabled_values': enabled_values,
            'products': self.serialize_products(products)[start: end]
            }


    def serialized(self, start, end):
        return {
            'product_count': self.product_count,
            'facets': [facet.serialize_self() for facet in self.facets],
            'enabled_values': self.enabled_values,
            'products': self.serialize_products(self.products)[start: end]
            }


    def serialize_products(self, products):
        if not products:
            return []
        imageurl = get_storage_class().base_path()
        return products.annotate(
            swatch_url=Concat(Value(imageurl), 'swatch_image', output_field=CharField())
            ).values(
                'pk',
                'unit',
                'manufacturer_style',
                'manufacturer_collection',
                'manufacturer_sku',
                'name',
                'hash_value',
                'swatch_url',
                'swatch_image',
                'manufacturer__label',
                'low_price'
                )
                # )[self.start: self.end]


class Sorter:

    def __init__(self, product_type, request: Request, supplier_pk=None):
        self.product_type = product_type
        self.request = request
        # self.page = 1
        # self.page_size = 20
        self.query_index: QueryIndex = None
        self.supplier_pk = supplier_pk
        self.facets = load_facets(product_type, supplier_pk)
        self.initial_products = self.get_products()
        self.initial_product_count = int(self.initial_products.count())
        # self.path_key = None
        self.content = self.__process_request()

    # @property
    # def page_start(self):
    #     return (self.page - 1) * self.page_size

    # @property
    # def page_end(self):
    #     return self.page * self.page_size


    @property
    def data(self):
        return self.content


    @property
    def serialized(self):
        return self.content.serialized


    def get_products(self):
        if self.supplier_pk:
            pks = SupplierProduct.objects.filter(location__pk=self.supplier_pk).values_list(
                'product__pk', flat=True)
            return self.product_type.objects.filter(pk__in=pks)
        return self.product_type.objects.all()


    @transaction.atomic
    def __process_request(self):
        query_dict: QueryDict = QueryDict(self.request.GET.urlencode(), mutable=True)
        # if 'page' in query_dict:
        #     self.page = query_dict.pop('page')
        # if 'search' in query_dict:
        #     search_string = query_dict.pop('search')
        # self.path_key = self.request.path + query_dict.urlencode()
        # res = cache.get(self.path_key)
        # if res:
        #     return res.serialize_self(self.page_start, self.page_end)
        for facet in self.facets:
            query_dict = facet.parse_request(query_dict)
        query_index, created = QueryIndex.objects.get_or_create_qi(
            query_path=self.request.path,
            query_dict=query_dict.urlencode(),
            retailer_location=self.supplier_pk
            )
        self.query_index = query_index
        if query_index.dirty or created:
            static_queryset = self.build_query_index()
            return self.calculate_response(static_queryset)
        return self.calculate_response()


    def build_query_index(self):
        pk_sets = [facet.filter_self() for facet in self.facets if facet and not facet.dynamic]
        pk_sets = [pks for pks in pk_sets if pks and len(pks) < self.initial_product_count]
        prods = self.initial_products
        for pks in pk_sets:
            prods = prods.filter(pk__in=pks)
        pks = list(prods.values_list('pk', flat=True))
        self.query_index.add_products(pks)
        return prods


    def calculate_response(self, static_queryset: QuerySet = None):
        if not static_queryset:
            pks = self.query_index.get_product_pks()
            static_queryset = self.initial_products.filter(pk__in=pks)
        pk_sets = [facet.filter_self() for facet in self.facets if facet and facet.dynamic]
        pk_sets = [pks for pks in pk_sets if pks is not None and len(pks) < self.initial_product_count]
        dynamic_queryset = self.initial_products
        for pks in pk_sets:
            dynamic_queryset = dynamic_queryset.filter(pk__in=pks)
        static_enabled_values = [facet.count_self(self.query_index.pk, self.facets, dynamic_queryset) for facet in self.facets if not facet.dynamic]
        dynamic_enabled_values = [facet.count_self(self.query_index.pk, self.facets, static_queryset) for facet in self.facets if facet.dynamic]
        enabled_values = static_enabled_values + dynamic_enabled_values
        enabled_values = [facet for facet in enabled_values if facet]
        products = dynamic_queryset.intersection(static_queryset).values_list('pk', flat=True)
        products = self.initial_products.filter(pk__in=products)
        innis = list(itertools.chain.from_iterable(enabled_values))
        product_count = len(products)
        products = Product.objects.select_related('manufacturer').filter(pk__in=products).product_prices()
        return FilterResponse(product_count, self.facets, products, innis)

