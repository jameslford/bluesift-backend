import itertools
from typing import List
from dataclasses import field as dfield
from rest_framework.request import Request
from django.core.files.storage import get_storage_class
from django.db.models.functions import Concat
from django.http import QueryDict
from django.db.models.query import QuerySet, Value
from django.db.models import CharField
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from Suppliers.models import SupplierProduct
from Products.models import Product
from .models import (
    AvailabilityFacet,
    BaseFacet,
    QueryIndex,
    )


class FilterResponse:
    def __init__(self):
        self.legit_queries: List[str] = dfield(default_factory=list)
        self.product_count: int = 0
        self.facets: List[dict] = []
        self.products: List[dict] = None


    def asdict(self):
        return {
            'legit_queries': self.legit_queries,
            'product_count': self.product_count,
            'facets': self.facets,
            'products': self.products,
        }
    # page: int = 1
    # load_more: bool = True
    # return_products: bool = True
    # message: Message = None
    # filter_dict: List[dict] = None
    # enabled_values: List[EnabledValue] = dfield(default_factory=list)





class Sorter:

    def __init__(self, product_type, request: Request, supplier_pk=None):
        self.product_type = product_type
        self.request = request
        self.query_index: QueryIndex = None
        self.supplier_pk = supplier_pk
        self.products = self.get_products()
        avi_facet = [AvailabilityFacet(self.supplier_pk)]
        model_types = self.product_type._meta.get_parent_list() + [self.product_type]
        parents = [ContentType.objects.get_for_model(mod) for mod in model_types]
        self.facets: List[BaseFacet] = avi_facet + list(BaseFacet.subclasses.filter(content_type__in=parents).select_subclasses())


    @property
    def data(self):
        return self.__process_request()


    def get_products(self, select_related='manufacturer'):
        if self.supplier_pk:
            pks = SupplierProduct.objects.filter(location__pk=self.supplier_pk).values_list(
                'product__pk', flat=True)
            return self.product_type.objects.all().prefetch_related(
                'priced').select_related(select_related).filter(pk__in=pks).product_prices(self.supplier_pk)
        return self.product_type.objects.select_related(select_related).all().product_prices()


    @transaction.atomic
    def __process_request(self):
        query_dict: QueryDict = QueryDict(self.request.GET.urlencode(), mutable=True)
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


    def calculate_response(self, static_queryset: QuerySet = None):
        # import itertools
        if not static_queryset:
            pks = self.query_index.get_product_pks()
            static_queryset = self.product_type.objects.filter(pk__in=pks).product_prices()
        print('filtering dynamic -----------------------------------------')
        dynamic_queryset = [
            facet.filter_self(self.products) for facet in self.facets if facet and facet.dynamic
            ]
        products = static_queryset.intersection(*dynamic_queryset).values_list('pk', flat=True)
        # force the queryset to evalute here so that it can be renewed on the annoate call later
        product_count = len(products)
        products = Product.objects.select_related('manufacturer').filter(pk__in=products).product_prices()
        for facet in self.facets:
            facet.count_self(self.query_index.pk, self.products, self.facets)
        serialized_facets = [facet.serialize_self() for facet in self.facets]
        enabled_values = [facet.enabled_values for facet in self.facets if facet]
        enabled_values = list(itertools.chain.from_iterable(enabled_values))
        print(enabled_values)
        return {
            'product_count': product_count,
            'facets': serialized_facets,
            'enabled_values': enabled_values,
            'products': self.serialize_products(products),
            }
            # static_queryset = self.query_index.products.all()
        # enabled_values = list(itertools.chain.from_iterable(enabled_values))
        # enabled_values = [a.asdict() for a in enabled_values]
        # enabled_values = [self.get_enabled_values(facet) for facet in self.facets if facet]


    def build_query_index(self):
        static_querysets = [
            facet.filter_self(self.products) for facet in self.facets if not facet.dynamic
            ]
        new_prods = self.products.intersection(*static_querysets).values_list('pk', flat=True)
        self.query_index.products.clear()
        self.query_index.products.add(*new_prods)
        self.query_index.save()
        return self.products.filter(pk__in=new_prods)


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



        # availability_facet = self.calculate_availability_facet(products)
    # def calculate_availability_facet(self, ):

    #     pass
            # if facet.initially_counted:

        # counted_querysets = [
        #     facet.filter_self(products) for facet in self.facets if facet.used_in_initial_calculation
        #     ]
        # counted_querysets = [qset for qset in counted_querysets if qset.coun]
        # for facet in self.facets:
        #     facet.set_intersection(self.query_index.pk, products, self.facets)


# """
# Primarily 2 classes that return product (not subclassed) instances
# """

# from dataclasses import dataclass, asdict
# from dataclasses import field as dfield
# from typing import List
# from django.db import models
# from django.core.files.storage import get_storage_class
# from django.contrib.postgres.search import SearchVector
# from django.contrib.gis.measure import D
# from django.db.models.query import QuerySet
# from django.db.models import Value, CharField
# from django.db.models.functions import Concat
# from django.http import HttpRequest, QueryDict
# from Addresses.models import Zipcode
# # from Products.serializers import serialize_product
# from Products.models import Product
# from Suppliers.models import SupplierProduct
# from .models import (
#     construct_range_facet,
#     return_radii,
#     ProductFilter,
#     QueryIndex,
#     Facet,
#     LocationFacet,
#     FacetValue,
#     FacetOthersCollection,
#     AVAILABILITY_FACET,
#     BOOLGROUP_FACET,
#     RANGE_FACET,
#     PRICE_FACET,
#     MULTITEXT_FACET,
#     MANUFACTURER_FACET,
#     LOCATION_FACET,
#     KEYTERM_FACET,
#     DEPENDENT_FACET,
#     COLOR_FACET
# )

# from .tasks import add_facet_others_delay



# @dataclass
# class EnabledValue:
#     query_value: str = None
#     read_value: str = None


# @dataclass
# class Message:
#     main: str = 'No results'
#     note: str = 'Please expand selection'


# @dataclass
# class FilterResponse:
#     legit_queries: List[str] = dfield(default_factory=list)
#     page: int = 1
#     load_more: bool = True
#     return_products: bool = True
#     message: Message = None
#     product_count: int = 0
#     filter_dict: List[dict] = None
#     enabled_values: List[EnabledValue] = dfield(default_factory=list)
#     products: List[dict] = None


# class Sorter:
#     """
#     Confusing af class - all functions are basically just steps used for the __call__ function:
#     """
#     def __init__(self, product_type, request: HttpRequest, update=False, location_pk=None):
#         self.request: HttpRequest = request
#         self.product_type = product_type
#         self.product_filter: ProductFilter = ProductFilter.get_filter(model=product_type)
#         self.location_pk = location_pk
#         self.update = update
#         self.response: FilterResponse = FilterResponse()
#         self.facets: List[Facet] = [Facet(**f_dict) for f_dict in self.product_filter.filter_dictionary]
#         self.query_index: QueryIndex = None
#         self.page = 1

# # ## Main thread is the next 4 functions. Everything below are functions used in their execution ###

#     # @transaction.atomic()
#     def __call__(self):
#         return self.__process_request()

#     def __process_request(self):
#         stripped_fields = {}
#         query_dict: QueryDict = QueryDict(self.request.GET.urlencode(), mutable=True)
#         for field in self.product_filter.floating_fields():
#             if field in query_dict:
#                 values = query_dict.pop(field)
#                 stripped_fields[field] = values
#         query_index, created = QueryIndex.objects.get_or_create_qi(
#             query_path=self.request.path,
#             query_dict=query_dict.urlencode(),
#             product_filter=self.product_filter,
#             retailer_location=self.location_pk
#             )
#         self.query_index = query_index
#         self.__parse_querydict(query_dict)
#         self.__check_dependents()
#         if query_index.dirty or self.update or created:
#             self.build_query_index()
#         if stripped_fields:
#             return self.filter_floating(stripped_fields)
#         return self.return_static_response()

#     def __parse_querydict(self, request_dict: QueryDict = None):
#         """
#         Associates query parameters with their respective facet,
#         this makes sure that all query parameters values are in the facet.values,
#         which has been instantiated from self.product_filter.filter_dict.
#         Keeps arbitrary user values from entering any farther into the code.
#         """
#         if not request_dict:
#             request_dict = QueryDict(self.query_index.query_dict)
#         for facet in self.facets:
#             qterms = request_dict.get(facet.quer_value, [])
#             if qterms:
#                 qterms = qterms.split(',')
#             facet.qterms = [term for term in qterms if term in facet.values]

#     def build_query_index(self, full_build=True):
#         """
#         Populates query index with products and json response.
#         The products it stores come from values that are not subject to much change,
#         so are used as a base for floating fields filtering
#         """
#         products = self.get_products()
#         self.__filter_bools(products)
#         self.__filter_multi(products)
#         self.assign_facet_others(products)
#         if full_build:
#             self.__count_objects(products)
#             indices = self.__get_counted_facet_indices()
#             qsets = [self.facets[q].queryset for q in indices]
#             products = products.intersection(*qsets)
#             self.__set_filter_dict()
#             self.query_index.products.clear()
#             self.query_index.products.add(*products)
#             self.query_index.response = asdict(self.response)
#             self.query_index.dirty = False
#             self.query_index.save()

#     def filter_floating(self, stripped_fields: dict):
#         """
#         Filters fields that are subject to rapid change - price, location, availability fields.
#         draws initial products from QueryIndex
#         """
#         self.__check_availability_facet(stripped_fields)
#         search_terms = stripped_fields.pop('search') if 'search' in stripped_fields else None
#         for key in stripped_fields:
#             index = self.get_index_by_qv(key)
#             if index is None:
#                 continue
#             facet: Facet = self.facets[index]
#             facet.qterms = stripped_fields[key]
#         products = self.get_products('manufacturer').product_prices(self.location_pk)
#         products = self.__filter_search_terms(products, search_terms) if search_terms else products
#         products = self.__filter_location(products)
#         products = self.__filter_range(products)
#         products = self.__filter_availability(products)
#         self.__count_objects(products)
#         qi_pks = self.query_index.get_product_pks()
#         products = products.filter(pk__in=qi_pks)
#         self.__count_availability(products)
#         self.response.product_count = products.count()
#         self.response.products = self.__serialize_products(products)
#         self.__set_filter_dict()
#         return asdict(self.response)

#     def return_static_response(self):
#         """
#         Returns a stored ('static') response from queries associated QueryIndex.
#         This is used when there are not 'floating fields' (availability, price, location).
#         However, it does need to check the counts for possible types of availability and insert them dynamically,
#         as these are subject to change
#         """
#         products = self.query_index.get_products('manufacturer').product_prices(self.location_pk)
#         self.__count_availability(products)
#         availability_facet = self.facets[self.get_index_by_qv('availability')]
#         self.response.product_count = products.count()
#         serialized_prods = self.__serialize_products(products)
#         response = self.query_index.response
#         response['product_count'] = products.count()
#         response['filter_dict'] = [asdict(availability_facet)] + response['filter_dict']
#         response['products'] = serialized_prods
#         return response

#     def __set_filter_dict(self):
#         legit_queries = []
#         for facet in self.facets:
#             facet.queryset = None
#             facet.intersection = None
#             if facet.qterms:
#                 for term in facet.qterms:
#                     query_expression = f'{facet.quer_value}={term}'
#                     legit_queries.append(query_expression)
#         self.response.legit_queries = list(set(legit_queries))
#         self.facets.sort(key=lambda x: x.order)
#         self.response.filter_dict = [asdict(qfacet) for qfacet in self.facets]

#     def get_products(self, select_related=None):
#         """ Returns applicable product subclass instances """
#         if self.location_pk:
#             pks = SupplierProduct.objects.filter(location__pk=self.location_pk).values_list('product__pk', flat=True)
#             return self.product_type.objects.all().prefetch_related('priced').filter(pk__in=pks)
#         if select_related:
#             return self.product_type.objects.select_related(select_related).all()
#         return self.product_type.objects.all()

#     def assign_facet_others(self, products):
#         """ holder """
#         indices = self.__get_counted_facet_indices()
#         for index in indices:
#             facet: Facet = self.facets[index]
#             if facet.facet_type == BOOLGROUP_FACET:
#                 other_qsets = [self.facets[q].queryset for q in indices]
#             else:
#                 other_qsets = [self.facets[q].queryset for q in indices if q != index]
#             facet.intersection = products.intersection(*other_qsets).values_list('pk', flat=True)
#             add_facet_others_delay.delay(self.query_index.pk, facet.name, list(facet.intersection))

#     def __count_objects(self, products: QuerySet):
#         indices = self.__get_counted_facet_indices()
#         for index in indices:
#             facet: Facet = self.facets[index]
#             if facet.intersection:
#                 foc = facet.intersection
#                 new_prods = products.filter(pk__in=foc)
#             else:
#                 foc = FacetOthersCollection.objects.filter(query_index=self.query_index, facet_name=facet.name).first()
#                 if foc:
#                     new_prods = products.filter(pk__in=foc.get_product_pks())
#                 else:
#                     self.build_query_index(False)
#                     new_prods = products.filter(pk__in=facet.intersection)
#             return_values = []
#             if facet.facet_type == BOOLGROUP_FACET:
#                 args = {value: models.Count(value, filter=models.Q(**{value: True})) for value in facet.values}
#                 bool_values = new_prods.aggregate(**args)
#                 for value in bool_values.items():
#                     name, count = value
#                     selected = bool(facet.qterms and name in facet.qterms)
#                     facet.total_count += count
#                     return_values.append(FacetValue(name, count, selected))
#                     if selected:
#                         facet.selected = True
#                 facet.return_values = return_values
#                 continue
#             values = list(new_prods.values(facet.quer_value).annotate(val_count=models.Count(facet.quer_value)))
#             for value in values:
#                 count = value['val_count']
#                 label = value[facet.quer_value]
#                 selected = bool(facet.qterms and label in facet.qterms)
#                 facet.total_count += count
#                 if selected:
#                     facet.selected = True
#                 return_values.append(FacetValue(label, count, selected))
#                 facet.return_values = return_values

# # ## utility functions below ###

#     def get_index_by_qv(self, keyword: str):
#         for count, facet in enumerate(self.facets):
#             facet: Facet = facet
#             if facet.quer_value == keyword:
#                 return count
#         return None

#     def get_indices_by_ft(self, facet_type: str) -> [int]:
#         indices = []
#         for count, facet in enumerate(self.facets):
#             if facet.facet_type == facet_type:
#                 indices.append(count)
#         return indices

#     def __check_availability_facet(self, stripped_fields):
#         if self.location_pk:
#             self.facets.append(Facet('retailer price', PRICE_FACET, 'in_store_ppu', total_count=1, order=2))
#             return
#         avail_facet: Facet = self.facets[self.get_indices_by_ft(AVAILABILITY_FACET)[0]]
#         qterms = stripped_fields.pop('availability') if 'availability' in stripped_fields else []
#         avail_facet.qterms = [term for term in qterms if term in Product.objects.safe_availability_commands()]
#         if not avail_facet.qterms:
#             return
#         self.facets.append(Facet('location', LOCATION_FACET, 'location', total_count=1, order=3))
#         self.facets.append(Facet('price', PRICE_FACET, 'low_price', total_count=1, order=2))

#     def __check_dependents(self):
#         kt_facet = self.get_indices_by_ft(KEYTERM_FACET)
#         if kt_facet and self.facets[kt_facet[0]].qterms:
#             return
#         facet_indices = self.get_indices_by_ft(DEPENDENT_FACET)
#         for index in sorted(facet_indices, reverse=True):
#             del self.facets[index]

#     def __serialize_products(self, products: QuerySet):
#         if not self.response.return_products:
#             return []
#         imageurl = get_storage_class().base_path()
#         return products.annotate(swatch_url=Concat(Value(imageurl), 'swatch_image', output_field=CharField())).values(
#             'pk',
#             'unit',
#             'manufacturer_style',
#             'manufacturer_collection',
#             'manufacturer_sku',
#             'name',
#             'hash_value',
#             'swatch_url',
#             'swatch_image',
#             'manufacturer__label',
#             'low_price'
#         )

#     def __filter_bools(self, products: QuerySet):
#         bool_indices = self.get_indices_by_ft(BOOLGROUP_FACET)
#         for index in bool_indices:
#             facet = self.facets[index]
#             if not facet.qterms:
#                 facet.qterms = []
#                 self.facets[index].queryset = products
#                 continue
#             facet.qterms = [term for term in facet.qterms if term in facet.values]
#             facet.selected = True
#             terms = {}
#             for term in facet.qterms:
#                 terms[term] = True
#                 facet.selected = True
#             facet.queryset = products.filter(**terms)

#     def __count_availability(self, products: QuerySet):
#         index = self.get_index_by_qv('availability')
#         if index is None:
#             return
#         facet: Facet = self.facets[index]
#         return_values = []
#         # getting pks means the full set does not evaluate for each iteration below
#         product_pks = products.values_list('pk')
#         for value in facet.values:
#             count = Product.objects.filter(pk__in=product_pks).filter_availability(value, self.location_pk).count()
#             facet.total_count += count
#             return_values.append(FacetValue(value, count, bool(facet.qterms and value in facet.qterms)))
#         facet.return_values = return_values

#     def __filter_availability(self, products: QuerySet):
#         index = self.get_index_by_qv('availability')
#         if index is None:
#             return products
#         facet: Facet = self.facets[index]
#         if facet.qterms:
#             facet.selected = True
#             products = products.filter_availability(facet.qterms, self.location_pk, True)
#             return products
#         return products

#     def __get_mt_indices(self):
#         mt_facets = self.get_indices_by_ft(MULTITEXT_FACET)
#         kt_index = self.get_indices_by_ft(KEYTERM_FACET)
#         color_index = self.get_indices_by_ft(COLOR_FACET)
#         manu_index = self.get_indices_by_ft(MANUFACTURER_FACET)
#         dep_index = self.get_indices_by_ft(DEPENDENT_FACET)
#         indices = mt_facets + kt_index + color_index + manu_index + dep_index
#         return indices

#     def __filter_multi(self, products: QuerySet):
#         indices = self.__get_mt_indices()
#         for index in indices:
#             facet = self.facets[index]
#             if not facet.qterms:
#                 self.facets[index].queryset = products
#                 continue
#             q_object = models.Q()
#             for term in facet.qterms:
#                 q_object |= models.Q(**{facet.quer_value: term})
#                 facet.selected = True
#             facet.queryset = products.filter(q_object)

#     def __filter_location(self, products: QuerySet):
#         loc_facet_index = self.get_index_by_qv('location')
#         if not loc_facet_index:
#             return products
#         self.facets[loc_facet_index].return_values = [LocationFacet(value='location', default_radii=return_radii())]
#         loc_facet = self.facets[loc_facet_index]
#         if not loc_facet.qterms:
#             return products
#         return_facet: LocationFacet = loc_facet.return_values[0]
#         rad_raw = [q for q in loc_facet.qterms if 'radius' in q]
#         zip_raw = [q for q in loc_facet.qterms if 'zip' in q]
#         if not (rad_raw and zip_raw):
#             return products
#         radius_int = int(rad_raw[-1].replace('radius-', ''))
#         return_facet.radius = radius_int
#         radius = D(mi=radius_int)
#         zipcode = zip_raw[-1].replace('zipcode-', '')
#         coords = Zipcode.objects.filter(code=zipcode).first().centroid.point
#         if not coords:
#             return_facet.zipcode = 'invalid zipcode'
#             return products
#         return_facet.zipcode = zipcode
#         return_facet.enabled = True
#         new_products = products.filter(locations__distance_lte=(coords, radius))
#         if not new_products:
#             self.response.message = Message(note='Expand location for more results')
#             self.response.return_products = False
#             self.response.load_more = False
#             return products
#         loc_facet.return_values = [return_facet]
#         loc_facet.selected = True
#         return products

#     def __range_iterator(self, products: QuerySet, index):
#         facet = self.facets[index]
#         _products, new_facet, contains_values = construct_range_facet(products, facet)
#         if not contains_values:
#             del self.facets[index]
#             return _products
#         self.facets[index] = new_facet
#         return _products

#     def __filter_range(self, products: QuerySet):
#         _products = products
#         range_indices = self.get_indices_by_ft(RANGE_FACET)
#         if range_indices:
#             for index in sorted(range_indices, reverse=True):
#                 _products = self.__range_iterator(_products, index)
#             return _products
#         price_indices = self.get_indices_by_ft(PRICE_FACET)
#         if not price_indices:
#             return _products
#         if self.location_pk:
#             sup_prods = products.supplier_products(self.location_pk)
#             sup_prods = self.__range_iterator(sup_prods, price_indices[0])
#             return self.product_type.objects.filter(pk__in=models.Subquery(sup_prods.values('product__pk')))
#         return self.__range_iterator(_products, price_indices[0])

#     def __filter_search_terms(self, products: QuerySet, search_term=None):
#         if not search_term:
#             return products
#         searched_prods = products.annotate(
#             search=SearchVector(
#                 'name',
#                 'manufacturer__label'
#             )
#         ).filter(search=search_term)
#         if not searched_prods:
#             self.response.return_products = False
#             self.response.load_more = False
#             self.response.message = Message(
#                 note='Test search produced no results. Make sure to use full words')
#             return products
#         return searched_prods

#     def __get_counted_facet_indices(self):
#         exclude_list = [RANGE_FACET, LOCATION_FACET, PRICE_FACET, AVAILABILITY_FACET]
#         indices = []
#         for count, _facet in enumerate(self.facets):
#             if _facet.facet_type not in exclude_list:
#                 indices.append(count)
#         return indices

#     def __return_no_products(self):
#         for index in self.__get_counted_facet_indices():
#             facet = self.facets[index]
#             if facet.values:
#                 facet.return_values = [
#                     FacetValue(
#                         value,
#                         0,
#                         bool(facet.qterms and value in facet.qterms)
#                         ) for value in facet.values
#                     ]
#         self.response.message = 'No results'

            # self._products = self.product_type.objects.all().prefetch_related(
            #     'priced').select_related(select_related).filter(pk__in=pks).product_prices(self.supplier_pk)
            # return self._products
        # if select_related:
        #     self._products = self.product_type.objects.select_related(select_related).all().product_prices()
        #     return self._products
        # self._products = self.product_type.objects.select_related(select_related).all().product_prices()
        # return self._products
