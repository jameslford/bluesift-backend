import itertools
from typing import List
from rest_framework.request import Request
from django.core.files.storage import get_storage_class
from django.core.cache import cache
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Concat
from django.http import QueryDict
from django.db.models.query import QuerySet, Value
from django.db.models import CharField
from django.db import transaction
from Suppliers.models import SupplierProduct
# from config.tasks import add_supplier_record
from config.globals import check_department_string
from Products.models import Product
from .models import (
    load_facets,
    BaseFacet,
    QueryIndex,
    )

page_size = 20


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
        cache.set(path_key, pickle_dict, 60 * 15)


    @classmethod
    def get_cache(cls, request: Request, product_type: str = None, sub_product: str = None):
        query_dict: QueryDict = QueryDict(request.GET.urlencode(), mutable=True)
        page = 0
        search_string = None
        location_pk = None
        if 'supplier_pk' in query_dict:
            location_pk = query_dict.get('supplier_pk', None)
            # add_supplier_record.delay(request.get_full_path(), pk=location_pk)
        if 'page' in query_dict:
            page = query_dict.pop('page')[0].split(',')[-1]
        if 'search' in query_dict:
            search_string = query_dict.pop('search')
        path_key = request.path + query_dict.urlencode()
        res_dict = cache.get(path_key)
        index = slice(page * page_size, (page + 1) * page_size)
        if res_dict:
            if search_string:
                product_pks = map(lambda x: x['pk'], res_dict['products'])
                products = Product.objects.annotate(
                    similarity=TrigramSimilarity('hash_value', search_string)
                    ).filter(similarity__gte=0.1, pk__in=product_pks).order_by('-similarity')[0:20]
                products = cls.serialize_products(products)
                res_dict['products'] = products
                res_dict['product_count'] = len(products)
                return res_dict
            prods = res_dict.get('products')
            if len(prods) <= (page + 1) * page_size:
                index = slice(None, None)
            res_dict['products'] = prods[index]
            res_dict['current_page'] = page
            return res_dict
        if sub_product:
            product_type = check_department_string(sub_product)
        elif product_type:
            product_type = check_department_string(product_type)
        else:
            product_type = Product
        if not product_type:
            return None
        content = Sorter(product_type, path=request.path, query_dict=query_dict, supplier_pk=location_pk).content
        content.set_cache(path_key)
        if content.product_count <= (page + 1) * page_size:
            index = slice(None, None)
        return content.serialized(index, page)


    def serialized(self, index, current_page):
        facets = [facet.serialize_self() for facet in self.facets]
        return {
            'product_count': self.product_count,
            'facets': [facet for facet in facets if facet],
            'enabled_values': self.enabled_values,
            'products': self.serialize_products(self.products)[index],
            'current_page': current_page
            }

    @classmethod
    def serialize_products(cls, products):
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


class Sorter:

    def __init__(self, product_type, path, query_dict, supplier_pk=None):
        self.product_type = product_type
        self.query_index: QueryIndex = None
        self.supplier_pk = supplier_pk
        self.facets = load_facets(product_type, supplier_pk)
        self.initial_products = self.get_products()
        self.initial_product_count = int(self.initial_products.count())
        self.content: FilterResponse = self.__process_request(query_dict, path)


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
    def __process_request(self, query_dict, path):
        for facet in self.facets:
            query_dict = facet.parse_request(query_dict)
        query_index, created = QueryIndex.objects.get_or_create_qi(
            query_path=path,
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
        # self.query_index.add_products(pks)
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
        innis = list(itertools.chain.from_iterable(enabled_values))
        product_count = len(products)
        products = Product.objects.select_related('manufacturer').filter(pk__in=products).product_prices()
        return FilterResponse(product_count, self.facets, products, innis)




        # self.request = request
        # self.page = 1
        # self.page_size = 20

    # @property
    # def page_start(self):
    #     return (self.page - 1) * self.page_size

    # @property
    # def page_end(self):
    #     return self.page * self.page_size


        # previous_page = page - 1
        # next_page = page + 1
        # page_start = previous_page * page_size
        # page_end = page * page_size
            # res_dict['previous_page'] = previous_page
            # res_dict['next_page'] = next_page

    # @classmethod
    # def get_cache(cls, path, start, end):
    #     res_dict = cache.get(path)
    #     if not res_dict:
    #         return None
    #     prods = res_dict.get('products')
    #     res_dict['products'] = prods[start: end]
    #     return res_dict


        # query_dict: QueryDict = QueryDict(self.request.GET.urlencode(), mutable=True)
        # if 'page' in query_dict:
        #     self.page = query_dict.pop('page')
        # if 'search' in query_dict:
        #     search_string = query_dict.pop('search')
        # self.path_key = self.request.path + query_dict.urlencode()
        # res = cache.get(self.path_key)
        # if res:
        #     return res.serialize_self(self.page_start, self.page_end)

    # def serialize_cached(self, product_count, facets, enabled_values, products, start, end):
    #     return {
    #         'product_count': product_count,
    #         'facets': facets,
    #         'enabled_values': enabled_values,
    #         'products': self.serialize_products(products)[start: end]
    #         }
