''' Products.views.py '''


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.pagination import PageNumberPagination
# from .scripts import FilterSorter
# from .serializers import ProductDetailSerializer, SerpyProduct
from .models import Product
from .sorter import DetailSorter, FilterSorter
# from Profiles.serializers import SupplierProductMiniSerializer

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
