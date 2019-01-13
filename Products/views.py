''' Products.views.py '''
import math
from decimal import Decimal
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .scripts import FilterSorter
from .serializers import ProductSerializer, ProductDetailSerializer
from .models import Product


@api_view(['GET'])
def product_list(request):
    # products = Product.objects.all()
    # serialized = ProductSerializer(products, many=True)
    # return Response(serialized.data)

    request_url = request.GET.urlencode().split('&')
    # print('wonkeyr', request_url)
    request_url = [query for query in request_url if 'page' not in query]
    queries = request.GET.getlist('quer')
    page = request.GET.get('page', 1)
    sorter = FilterSorter(queries, request_url)

    products = Product.objects.all()
    # filters applications, availability and location. nothing special
    products = sorter.filter_bools(products)
    products = sorter.filter_location(products)
    products = sorter.filter_price(products)
    # filters manu, size, thickness, and look - and arg between groups, or arg within groups
    products = sorter.filter_attribute(products)
    # products = sorter.filter_materials_down(products)

    filter_response = sorter.return_filter(products)

    paginator = PageNumberPagination()
    paginator.page_size = 12
    products_response = paginator.paginate_queryset(products, request)
    product_count = products.count() if products else 0
    page_count = math.ceil(product_count/paginator.page_size)
    load_more = True
    if page:
        page_number = int(page)
    else:
        page_number = 1
    if page_number == page_count:
        load_more = False

    serialized_products = ProductSerializer(products_response, many=True)
    legit_queries = ['quer=' + q for q in sorter.legit_queries]
    material_selected = sorter.spec_mat_facet

    content = {
        'load_more': load_more,
        'product_count': product_count,
        'material_selected': material_selected,
        'query': legit_queries,
        'current_page': page,
        'filter': filter_response,
        'products': serialized_products.data
    }

    return Response(content, status=status.HTTP_200_OK)







    # if not sorter.mat_queries:
    #     pass  # need to return response here
    # material_id = sorter.mat_queries[0]
    # material = Material.objects.filter(id=material_id).first()
    # if not material:
    #     pass  # need to return response here
    # products = products.filter(material=material)

    # if fin_queries:
    #     fin_prods = or_list_query(products, fin_queries, fin)

    # if surtex_queries:
    #     surtex_prods = or_list_query()


    # location_facet = None
    # if avail_queries_raw:
    #     radii = [5, 10, 20, 50, 100, 200]
    #     location_facet = {'name': 'Location', 'zip': zipcode, 'values': []}
    #     for radi in radii:
    #         value = {
    #             'radius': radi,
    #             'enabled': True if radi == radius_raw else False
    #         }
    #         location_facet['values'].append(value)

    # return Response('hallo')

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
