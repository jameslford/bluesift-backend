''' Products.views.py '''

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from FinishSurfaces.models import FinishSurface
from .models import Product, Manufacturer
from .sorter import DetailSorter, FilterSorter


@api_view(['GET'])
def product_list(request, cat):
    sorter = FilterSorter(request, cat)
    content = sorter.return_content()
    return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_product(request, pk):
    product = Product.objects.filter(pk=pk).first()
    if not product:
        return Response('Invalid PK', status=status.HTTP_400_BAD_REQUEST)
    sorter = DetailSorter(product)
    return Response(sorter.content, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes(IsAdminUser)
def add_product(request):
    auth_header = request.META.get('custom_auth_header')
    if not auth_header:
        return Response('invalid', status=status.HTTP_400_BAD_REQUEST)
    if auth_header != 'klein-brothers':
        return Response('invalid', status=status.HTTP_400_BAD_REQUEST)
    data = request.data
    for item in data:
        product = Product()
        product.name = data.pop('name')
        product.bb_sku = data.pop('bb_sku')
        product.manufacturer_sku = data.pop('manufacturer_sku')
        product.manu_collection = data.pop('manufacturer_collection')
        product.manufacturer_style = data.pop('manufacturer_style')
        manu_name = data.pop('manufacturer_name')
        manufacturer = Manufacturer.objects.get_or_create(label=manu_name)
        product.manufacturer = manufacturer
        product.manufacturer_url = data.pop('product_url')
        product.commercial = data.pop('commercial')



