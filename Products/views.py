''' Products.views.py '''
import math
import googlemaps
from decimal import Decimal
# from pygeocoder import Geocoder
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from config.management.zips import lookup
import csv


from .serializers import(
    ProductSerializer,
    ProductDetailSerializer
    )

from .models import(
    Product,
    Build,
    Material,
    Manufacturer,
    Category,
    Finish
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

    app = 'application'
    avail = 'availability'
    loc = 'location'
    manu = 'manufacturer'
    thk = 'thickness'
    fin = 'finish'
    cat = 'category'
    build = 'build'
    mat = 'material'

    request_url = request.GET.urlencode().split('&')
    request_url = [query for query in request_url if 'page' not in query]
    queries = request.GET.getlist('quer')
    page =  request.GET.get('page', 1)

    app_queries_raw = [q for q in queries if app in q]
    app_queries = [q.replace(app+'-', '') for q in app_queries_raw]

    avail_queries_raw = [q for q in queries if avail in q]
    avail_queries = [q.replace(avail+'-', '') for q in avail_queries_raw]

    loc_queries_raw = [q for q in queries if loc in q]
    loc_queries = [q.replace(loc+'-', '') for q in loc_queries_raw]

    build_queries_raw = [q for q in queries if build in q]
    build_queries = [int(q.strip(build+'-')) for q in build_queries_raw]

    mat_queries_raw = [q for q in queries if mat in q]
    mat_queries = [int(q.strip(mat+'-')) for q in mat_queries_raw]

    cat_queries_raw = [q for q in queries if cat in q]
    cat_queries = [int(q.strip(cat+'-')) for q in cat_queries_raw]

    manu_queries_raw = [q for q in queries if manu in q]
    manu_queries = [int(q.strip(manu+'-')) for q in manu_queries_raw]

    fin_queries_raw = [q for q in queries if fin in q]
    fin_queries = [int(q.strip(fin+'-')) for q in fin_queries_raw]

    thk_queries_raw = [q for q in queries if thk in q]
    thk_queries = [Decimal(q.strip(thk+'-')) for q in thk_queries_raw]

    products = Product.objects.all()
    bool_raw = app_queries_raw + avail_queries_raw

    for application in app_queries + avail_queries:
        if hasattr(Product, application):
            arg = {application: True}
            products = products.filter(**arg)
        else:
            bool_raw = [q for q in bool_raw if application not in q]

    zipcode = None
    rad_raw = None
    radius_raw = None
    coords = None
    distance = None
    if loc_queries:
        rad_raw = [q for q in loc_queries if 'radius' in q]
        zip_raw = [q for q in loc_queries if 'zip' in q]
        radius_raw = int(rad_raw[0].replace('radius-', ''))
        radius = D(mi=radius_raw)
        zipcode = zip_raw[0].replace('zipcode-', '')
        coords = Zipcode.objects.filter(code=zipcode).first().centroid.point
        if coords:
            products = products.filter(locations__distance_lte=(coords, radius))
        else:
            zipcode = 'error'



    location_facet = None
    if avail_queries_raw:
        radii = [5, 10, 20, 50, 100, 200]
        location_facet = {'name': 'Location', 'zip': zipcode , 'values': []}
        for radi in radii:
            value = {
                'radius': radi,
                'enabled': True if radi == radius_raw else False
            }
            location_facet['values'].append(value)





    pcat_prods = or_list_query(products, cat_queries, 'build__category') if cat_queries else None
    pbuild_prods = or_list_query(products, build_queries, 'build') if build_queries else None
    pmat_prods = or_list_query(products, mat_queries, 'material') if mat_queries else None
    pmanu_prods = or_list_query(products, manu_queries, 'manufacturer') if manu_queries else None
    pfin_prods = or_list_query(products, fin_queries, 'finish') if fin_queries else None
    pthk_prods = or_list_query(products, thk_queries, 'thickness') if thk_queries else None

    prod_sets = [
        pcat_prods,
        pbuild_prods,
        pmat_prods,
        pmanu_prods,
        pfin_prods,
        pthk_prods
    ]

    avai_terms = ['for_sale_online', 'for_sale_in_store']
    app_terms = ['walls', 'countertops', 'floors', 'cabinet_fronts', 'shower_floors', 'shower_walls', 'exterior', 'covered', 'pool_linings']

    avai_facets = bool_facet(products, prod_sets, avail, avai_terms, avail_queries)
    app_facets = bool_facet(products, prod_sets, app, app_terms, app_queries)

    all_cats = Category.objects.all()
    cat_facets = facet(products, [pbuild_prods, pmat_prods, pmanu_prods, pfin_prods, pthk_prods], all_cats, 'build__category', cat, cat_queries)

    all_builds = Build.objects.all()
    build_facets = facet(products, [pcat_prods, pmat_prods, pmanu_prods, pfin_prods, pthk_prods], all_builds, 'build', build, build_queries)

    all_mats = Material.objects.all()
    mat_facets = facet(products, [pcat_prods, pbuild_prods, pmanu_prods, pfin_prods, pthk_prods], all_mats, 'material', mat, mat_queries)

    all_manu = Manufacturer.objects.all()
    manu_facets = facet(products, [pcat_prods, pbuild_prods, pmat_prods, pfin_prods, pthk_prods], all_manu, 'manufacturer', manu, manu_queries)

    all_fin = Finish.objects.all()
    fin_facets = facet(products, [pcat_prods, pbuild_prods, pmanu_prods, pmat_prods, pthk_prods], all_fin, 'finish', fin, fin_queries)

    final_list = [q for q in prod_sets if q]
    product_final = products.intersection(*final_list) if final_list else products

    paginator = PageNumberPagination()
    paginator.page_size = 12
    products_response = paginator.paginate_queryset(product_final, request)
    product_count = product_final.count()
    page_count = math.ceil(product_count/paginator.page_size)
    load_more = True
    if page:
        page_number = int(page)
    else:
        page_number = 1
    if page_number == page_count:
        load_more = False

    facet_list = [
        avai_facets,
        app_facets,
        cat_facets,
        build_facets,
        mat_facets,
        manu_facets,
        fin_facets
        ]

    serialized_products = ProductSerializer(products_response, many=True)
    raw_queries = [
        bool_raw +
        manu_queries_raw +
        thk_queries_raw +
        fin_queries_raw +
        cat_queries_raw +
        build_queries_raw +
        mat_queries_raw
    ]
    query_response = ['quer=' + q for q in raw_queries[0]]
    return Response({
        'product_count': product_count,
        'query' : query_response,
        # 'origin' :str(distance.m),
        'radius': radius_raw,
        'load_more': load_more,
        'current_page': page,
        'location': location_facet,
        'filter': facet_list,
        'products': serialized_products.data
        })


@api_view(['GET'])
def get_product(request, pk):
    product = Product.objects.get(id=pk)
    serialized_product = ProductDetailSerializer(product)
    return Response({'product': serialized_product.data})
