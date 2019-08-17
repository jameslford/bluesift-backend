"""
Primarily 2 classes that return product (not subclassed) instances
"""

import pdb
import copy
from dataclasses import dataclass, asdict
from dataclasses import field as dfield
from typing import List
from django.db import models, transaction
from django.contrib.postgres.search import SearchVector
from django.contrib.gis.measure import D
from django.db.models.query import QuerySet
from django.http import HttpRequest, QueryDict
from Addresses.models import Zipcode
from Products.serializers import SerpyProduct
from Products.models import Product, ProductSubClass
from UserProducts.serializers import RetailerProductMiniSerializer
from UserProducts.models import RetailerProduct
from ProductFilter.models import (
    construct_range_facet,
    return_radii,
    ProductFilter,
    QueryIndex,
    Facet,
    LocationFacet,
    FacetValue,
    FacetOthersCollection,
    AVAILABILITY_FACET,
    BOOLGROUP_FACET,
    RANGE_FACET,
    PRICE_FACET,
    MULTITEXT_FACET,
    MANUFACTURER_FACET,
    LOCATION_FACET,
    KEYTERM_FACET,
    DEPENDENT_FACET,
    COLOR_FACET
)



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
    enabled_values: List[str] = dfield(default_factory=list)
    products: List[dict] = None


class Sorter:
    """
    Confusing af class - all functions are basically just steps used for the __call__ function:

    """
    def __init__(self, product_type: ProductSubClass, request: HttpRequest, update=False, location_pk=None):
        self.request: HttpRequest = request
        self.product_type = product_type
        self.product_filter: ProductFilter = ProductFilter.get_filter(model=product_type)
        self.location_pk = location_pk
        self.update = update
        self.update = update
        self.response: FilterResponse = FilterResponse()
        self.facets: List[Facet] = [Facet(**f_dict) for f_dict in self.product_filter.filter_dictionary]
        self.query_index: QueryIndex = None

### Main thread is the next 4 functions. Everything below are functions used in their execution ###

    @transaction.atomic()
    def __call__(self):
        return self.__process_request()

    def __process_request(self):
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
        self.__parse_querydict(query_dict)
        self.__check_dependents()
        if query_index.dirty or self.update or created:
            self.build_query_index()
        if stripped_fields:
            return self.filter_floating(stripped_fields)
        return self.return_static_response()

    def __parse_querydict(self, request_dict: QueryDict = None):
        if not request_dict:
            request_dict = QueryDict(self.query_index.query_dict)
        for facet in self.facets:
            qterms = request_dict.getlist(facet.quer_value, [])
            facet.qterms = [term for term in qterms if term in facet.values]

    def build_query_index(self):
        """
        Populates query index with products and json response.
        The products it stores come from values that are not subject to much change,
        so are used as a base for floating fields filtering
        """
        products = self.get_products()
        self.__filter_bools(products)
        self.__filter_multi(products)
        self.assign_facet_others(products)
        self.__count_objects(products)
        indices = self.__get_counted_facet_indices()
        qsets = [self.facets[q].queryset for q in indices]
        products = products.intersection(*qsets)
        self.__set_filter_dict()
        self.query_index.products.clear()
        self.query_index.products.add(*products)
        self.query_index.response = asdict(self.response)
        self.query_index.dirty = False
        self.query_index.save()


    def filter_floating(self, stripped_fields: dict):
        """
        Filters fields that are subject to rapid change - price, location, availability fields.
        draws initial products from QueryIndex
        """
        print('filtering floating')
        self.__check_availability_facet(stripped_fields)
        search_terms = stripped_fields.pop('search') if 'search' in stripped_fields else None
        for key in stripped_fields:
            index = self.get_index_by_qv(key)
            if index is None:
                continue
            facet: Facet = self.facets[index]
            facet.qterms = stripped_fields[key]
        products = self.get_products('manufacturer').product_prices(self.location_pk)
        products = self.__filter_search_terms(products, search_terms) if search_terms else products
        products = self.__filter_location(products)
        products = self.__filter_range(products)
        #!! need to fix line below - filtering correctly, but counting objects before they've been filtered by
        #!! qi intersection - either optionally include availability count in count objects or
        #!! mkae seperate count_availability function
        products = self.__filter_availability(products)
        self.__count_objects(products)
        qi_pks = self.query_index.get_product_pks()
        products = products.filter(pk__in=qi_pks)
        self.response.product_count = products.count()
        self.response.products = self.__serialize_products(products)
        self.__set_filter_dict()
        return asdict(self.response)

    def return_static_response(self):
        """
        Returns a stored ('static') response from queries associated QueryIndex.
        This is used when there are not 'floating fields' (availability, price, location).
        However, it does need to check the counts for possible types of availability and insert them dynamically,
        as these are subject to change
        """
        print('returning static')
        products = self.query_index.get_products('manufacturer').product_prices(self.location_pk)
        products = self.__filter_availability(products)
        availability_facet = self.facets[self.get_index_by_qv('availability')]
        self.response.product_count = products.count()
        serialized_prods = self.__serialize_products(products)
        response = self.query_index.response
        response['product_count'] = products.count()
        response['filter_dict'] = [asdict(availability_facet)] + response['filter_dict']
        response['products'] = serialized_prods
        return response

    def __set_filter_dict(self):
        enabled_values = []
        legit_queries = []
        for facet in self.facets:
            facet.queryset = None
            facet.intersection = None
            if facet.qterms:
                for term in facet.qterms:
                    query_expression = f'{facet.quer_value}={term}'
                    legit_queries.append(query_expression)
                    value_index = [count for count, item in enumerate(facet.return_values) if item.value == term]
                    if not value_index:
                        value_index = [0]
                    enabled_display_values = facet.return_values[value_index[0]].value
                    enabled_values.append(tuple([query_expression, enabled_display_values]))
        self.response.legit_queries = list(set(legit_queries))
        self.response.enabled_values = list(set(enabled_values))
        self.facets.sort(key=lambda x: x.order)
        self.response.filter_dict = [asdict(qfacet) for qfacet in self.facets]

    def get_products(self, select_related=None):
        """ Returns applicable product subclass instances """
        if self.location_pk:
            pks = RetailerProduct.objects.filter(retailer__pk=self.location_pk).values_list('product__pk', flat=True)
            return self.product_type.objects.all().prefetch_related('priced').filter(pk__in=pks)
        if select_related:
            return self.product_type.objects.select_related(select_related).all()
        return self.product_type.objects.all()

    def assign_facet_others(self, products):
        """ holder """
        indices = self.__get_counted_facet_indices()
        for index in indices:
            facet: Facet = self.facets[index]
            if not facet.queryset:
                continue
            foc, created = FacetOthersCollection.objects.get_or_create(query_index=self.query_index, facet_name=facet.name)
            if created or self.update:
                other_qsets = [self.facets[q].queryset for q in indices if q and q != index]
                facet.intersection = products.intersection(*other_qsets)
                foc.assign_new_products(facet.intersection.values_list('pk', flat=True))

        ###!!!  replace with function below to FacetOthersCollection on a celery delay !!!###
                # foc.assign_new_products_delay(new_prods.values_list('pk', flat=True))


    def __count_objects(self, products: QuerySet):
        indices = self.__get_counted_facet_indices()
        for index in indices:
            facet: Facet = self.facets[index]
            foc = FacetOthersCollection.objects.filter(query_index=self.query_index, facet_name=facet.name).first()
            new_prods = products.filter(pk__in=foc.get_product_pks())
            return_values = []
            if facet.facet_type == BOOLGROUP_FACET:
                args = {value: models.Count(value, filter=models.Q(**{value: True})) for value in facet.values}
                bool_values = new_prods.aggregate(**args)
                for value in bool_values.items():
                    name, count = value
                    selected = bool(facet.qterms and name in facet.qterms)
                    facet.total_count += count
                    return_values.append(FacetValue(name, count, selected))
                    if selected:
                        facet.selected = True
                facet.return_values = return_values
                continue
            values = list(new_prods.values(facet.quer_value).annotate(val_count=models.Count(facet.quer_value)))
            for value in values:
                count = value['val_count']
                label = value[facet.quer_value]
                selected = bool(facet.qterms and label in facet.qterms)
                facet.total_count += count
                if selected:
                    facet.selected = True
                return_values.append(FacetValue(label, count, selected))
                facet.return_values = return_values

### utility functions below ###

    def get_index_by_qv(self, keyword: str):
        for count, facet in enumerate(self.facets):
            facet: Facet = facet
            if facet.quer_value == keyword:
                return count
        return None

    def get_indices_by_ft(self, facet_type: str) -> [int]:
        indices = []
        for count, facet in enumerate(self.facets):
            if facet.facet_type == facet_type:
                indices.append(count)
        return indices

    def __check_availability_facet(self, stripped_fields):
        if self.location_pk:
            self.facets.append(Facet('retailer price', PRICE_FACET, 'in_store_ppu', total_count=1, order=2))
            return
        avail_facet: Facet = self.facets[self.get_indices_by_ft(AVAILABILITY_FACET)[0]]
        qterms = stripped_fields.pop('availability') if 'availability' in stripped_fields else []
        avail_facet.qterms = [term for term in qterms if term in Product.objects.safe_availability_commands()]
        if not avail_facet.qterms:
            return
        self.facets.append(Facet('location', LOCATION_FACET, 'location', total_count=1, order=3))
        self.facets.append(Facet('price', PRICE_FACET, 'low_price', total_count=1, order=2))

    def __check_dependents(self):
        kt_facet = self.get_indices_by_ft(KEYTERM_FACET)
        if kt_facet and self.facets[kt_facet[0]].qterms:
            return
        facet_indices = self.get_indices_by_ft(DEPENDENT_FACET)
        for index in sorted(facet_indices, reverse=True):
            del self.facets[index]

    def __serialize_products(self, products: QuerySet):
        if not self.response.return_products:
            return []
        return SerpyProduct(products, many=True).data


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
            # q_object = models.Q()
            terms = {}
            for term in facet.qterms:
                terms[term] = True
                # q_object |= models.Q(**{term: True})
                facet.selected = True
            # facet.queryset = products.filter(q_object)
            facet.queryset = products.filter(**terms)

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
            return self.product_type.objects.filter(pk__in=models.Subquery(sup_prods.values('product__pk')))
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
    pk: str
    unit: str = None
    manufacturer: str = None
    manufacturer_url: str = None
    manufacturer_sku: str = None
    manufacturer_collection: str = None
    manufacturer_style: str = None
    swatch_image: str = None
    room_scene: str = None
    priced: List = None
    lists: List[DetailListItem] = None


class DetailBuilder:

    def __init__(self, pk: str):
        self.bb_sku = pk
        self.product = self.get_subclass_instance()
        self.response: DetailResponse = DetailResponse(pk=str(self.product.pk))

    def get_subclass_instance(self):
        product = Product.subclasses.filter(pk=self.bb_sku).select_subclasses().first()
        if not product:
            raise Exception('no product found for ' + self.bb_sku)
        return product

    def get_product_filter(self) -> ProductFilter:
        return ProductFilter.get_filter(self.product)

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
                group_vals = [
                    {'term': attr, 'value': getattr(self.product, attr)} for attr in group_attrs if getattr(self.product, attr)
                    ]
                groups_list.append(DetailListItem(group_name, group_vals))
        return groups_list

    def assign_response(self):
        self.response.lists = self.get_bool_groups()
        details_list = self.get_stock_details() + self.get_subclass_remaining()
        self.response.lists.append(DetailListItem('details', details_list))
        self.response.priced = self.get_priced()
        self.response.manufacturer = self.product.manufacturer_name()
        self.response.manufacturer_url = self.product.manufacturer_url
        self.response.manufacturer_sku = self.product.manufacturer_sku
        self.response.manufacturer_collection = self.product.manu_collection
        self.response.manufacturer_style = self.product.manufacturer_style
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
