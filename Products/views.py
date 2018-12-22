''' Products.views.py '''
import math
import googlemaps
from decimal import Decimal
from django.conf import settings
from django.contrib.gis.geos import Point
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .scripts import avai_terms, app_terms, FilterSorter
from .serializers import (
    ProductSerializer,
    ProductDetailSerializer
    )
from .models import (
    Product,
    Material,
    Manufacturer,
    )
from Addresses.models import Zipcode

def or_list_query(products, args, term):
    _products = products
    if args:
        first_search = {term: args[0]}
        new_prods = products.filter(**first_search)
        for arg in args[1:]:
            next_search = {term: arg}
            new_prods = new_prods | products.filter(**next_search)
        return new_prods
    return _products

def bool_facet(products, qlist, name, facet_list, queries):
    # all_prods = Product.objects.all()
    new_list = [q for q in qlist if q]
    facet_dict = {'name': name, 'values': []}
    for item in facet_list:
        search = {item: True}
        item_prods = products.filter(**search)
        new_prods = item_prods.intersection(*new_list)
        value = {
            'label': item,
            'count': new_prods.count(),
            'enabled': item in queries,
            'value': item}
        facet_dict['values'].append(value)
    return facet_dict

def facet(products, qlist, facet_list, filter_term, name, queries):

    new_list = [q for q in qlist if q]
    facet_dict = {'name': name, 'values': []}
    for item in facet_list:
        search = {filter_term: item.id}
        item_prods = products.filter(**search)
        new_prods = item_prods.intersection(*new_list)
        value = {
            'listcount': len(qlist),
            'label': item.label,
            'count': new_prods.count(),
            'enabled': item.id in queries,
            'value': item.id}
        facet_dict['values'].append(value)
    return facet_dict

@api_view(['GET'])
def product_list(request):

    request_url = request.GET.urlencode().split('&')
    request_url = [query for query in request_url if 'page' not in query]
    queries = request.GET.getlist('quer')
    page = request.GET.get('page', 1)
    sorter = FilterSorter(queries)

    products = Product.objects.all()
    products = sorter.filter_bools(products)
    products = sorter.filter_location(products)

    

    if sorter.mat_queries:
        material_id = sorter.mat_queries[0]
        material = Material.objects.filter(id=material_id).first()
        if material:
            products = products.filter(material=material)


    if fin_queries:
        fin_prods = or_list_query(products, fin_queries, fin)

    if surtex_queries:
        surtex_prods = or_list_query()


    location_facet = None
    if avail_queries_raw:
        radii = [5, 10, 20, 50, 100, 200]
        location_facet = {'name': 'Location', 'zip': zipcode, 'values': []}
        for radi in radii:
            value = {
                'radius': radi,
                'enabled': True if radi == radius_raw else False
            }
            location_facet['values'].append(value)

    return Response('hallo')

    # pmat_prods = or_list_query(products, mat_queries, 'material') if mat_queries else None
    # pmanu_prods = or_list_query(products, manu_queries, 'manufacturer') if manu_queries else None
    # pthk_prods = or_list_query(products, thk_queries, 'thickness') if thk_queries else None

    # prod_sets = [
    #     pcat_prods,
    #     pbuild_prods,
    #     pmat_prods,
    #     pmanu_prods,
    #     pfin_prods,
    #     pthk_prods
    # ]

    # avai_facets = bool_facet(products, prod_sets, avail, avai_terms, avail_queries)
    # app_facets = bool_facet(products, prod_sets, app, app_terms, app_queries)

    # all_cats = Category.objects.all()
    # cat_facets = facet(products, [pbuild_prods, pmat_prods, pmanu_prods, pfin_prods, pthk_prods], all_cats, 'build__category', cat, cat_queries)

    # all_builds = Build.objects.all()
    # build_facets = facet(products, [pcat_prods, pmat_prods, pmanu_prods, pfin_prods, pthk_prods], all_builds, 'build', build, build_queries)

    # all_mats = Material.objects.all()
    # mat_facets = facet(products, [pcat_prods, pbuild_prods, pmanu_prods, pfin_prods, pthk_prods], all_mats, 'material', mat, mat_queries)

    # all_manu = Manufacturer.objects.all()
    # manu_facets = facet(products, [pcat_prods, pbuild_prods, pmat_prods, pfin_prods, pthk_prods], all_manu, 'manufacturer', manu, manu_queries)

    # all_fin = Finish.objects.all()
    # fin_facets = facet(products, [pcat_prods, pbuild_prods, pmanu_prods, pmat_prods, pthk_prods], all_fin, 'finish', fin, fin_queries)

    # final_list = [q for q in prod_sets if q]
    # product_final = products.intersection(*final_list) if final_list else products

    # paginator = PageNumberPagination()
    # paginator.page_size = 12
    # products_response = paginator.paginate_queryset(product_final, request)
    # product_count = product_final.count()
    # page_count = math.ceil(product_count/paginator.page_size)
    # load_more = True
    # if page:
    #     page_number = int(page)
    # else:
    #     page_number = 1
    # if page_number == page_count:
    #     load_more = False

    # facet_list = [
    #     avai_facets,
    #     app_facets,
    #     cat_facets,
    #     build_facets,
    #     mat_facets,
    #     manu_facets,
    #     fin_facets
    #     ]

    # serialized_products = ProductSerializer(products_response, many=True)
    # raw_queries = [
    #     bool_raw +
    #     manu_queries_raw +
    #     thk_queries_raw +
    #     fin_queries_raw +
    #     cat_queries_raw +
    #     build_queries_raw +
    #     mat_queries_raw
    # ]
    # query_response = ['quer=' + q for q in raw_queries[0]]
    # return Response({
    #     'product_count': product_count,
    #     'query' : query_response,
    #     # 'origin' :str(distance.m),
    #     'radius': radius_raw,
    #     'load_more': load_more,
    #     'current_page': page,
    #     'location': location_facet,
    #     'filter': facet_list,
    #     'products': serialized_products.data
    #     })


@api_view(['GET'])
def get_product(request, pk):
    product = Product.objects.get(id=pk)
    serialized_product = ProductDetailSerializer(product)
    return Response({'product': serialized_product.data})
