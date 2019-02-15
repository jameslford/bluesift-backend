''' Products.views.py '''
import math
import os
from decimal import Decimal
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from .scripts import FilterSorter
from .serializers import ProductSerializer, ProductDetailSerializer, SerpyProduct
from .models import Product
from Profiles.serializers import SupplierProductMiniSerializer


def set_perm():
    if os.environ['DJANGO_SETTINGS_MODULE'] == 'config.settings.staging':
        return IsAuthenticated
    else:
        return AllowAny


@api_view(['GET'])
@permission_classes((set_perm(),))
def product_list(request):

    request_url = request.GET.urlencode().split('&')
    request_url = [query for query in request_url if 'page' not in query]
    queries = request.GET.getlist('quer')
    search_terms = request.GET.getlist('search', None)
    page = request.GET.get('page', 1)
    sorter = FilterSorter(queries, search_terms, request_url)
    message = None
    return_products = True

    # products = Product.objects.select_related(*sorter.standalones.keys()).all()
    products = Product.objects.all()

    products = sorter.filter_location(products)
    products = sorter.filter_price(products)
    products = sorter.filter_thickness(products)

    products = sorter.filter_bools(products)
    products = sorter.filter_attribute(products)

    filter_response = sorter.return_filter(products)

    legit_queries = ['quer=' + q for q in sorter.legit_queries]
    paginator = PageNumberPagination()
    paginator.page_size = 24

    products = sorter.filter_search(products)

    products_response = paginator.paginate_queryset(products.prefetch_related('swatch_image'), request)
    product_count = products.count() if products else 0
    page_count = math.ceil(product_count/paginator.page_size)
    load_more = True
    if page:
        page_number = int(page)
        pg_str = 'page=' + str(page_number)
        sorter.legit_queries.append(pg_str)
    else:
        page_number = 1
    if page_number == page_count or not return_products:
        load_more = False

    serialized_products = SerpyProduct(products_response, many=True)
    # serialized_products = ProductSerializer(products_response.prefetch_related('swatch_image'), many=True)
    material_selected = sorter.spec_mat_facet

    content = {
        'load_more': load_more,
        'page_count': page_count,
        'product_count': product_count,
        'material_selected': material_selected,
        'query': legit_queries,
        'current_page': page,
        'message': message,
        'filter': filter_response,
        'products': serialized_products.data if return_products else []
    }

    return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_product(request, pk):
    user = request.user
    library = None
    if user.is_authenticated():
        locations = user.get_locations()
        loc_dict = [{'nickname': q.nickname, 'pk': q.pk } for q in locations]
    product = Product.objects.filter(pk=pk).first()
    if not product:
        return Response('Invalid PK', status=status.HTTP_400_BAD_REQUEST)
    online_priced = product.online_priced()
    online_priced = SupplierProductMiniSerializer(online_priced, many=True).data if online_priced else None
    in_store_priced = product.in_store_priced()
    in_store_priced = SupplierProductMiniSerializer(in_store_priced, many=True).data if in_store_priced else None
    serialized_product = ProductDetailSerializer(product)
    return Response(
        {
            'product': serialized_product.data,
            'in_store_priced': in_store_priced,
            'online_priced': online_priced,
            'locations': loc_dict
        }
        )
