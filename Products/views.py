''' Products.views.py '''
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from config.views import check_department_string
from ProductFilter.sorter import Sorter
from .models import Product


@api_view(['GET'])
def products_list(request: Request, product_type: str, location_pk: int = None, update=False):
    product_type = check_department_string(product_type)
    if not product_type:
        return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
    content = Sorter(product_type, request=request, location_pk=location_pk, update=update)
    return Response(content(), status=status.HTTP_200_OK)


@api_view(['GET'])
def product_detail(request, pk):
    response = Product.objects.get(pk=pk).serialize_detail()
    return Response(response, status=status.HTTP_200_OK)
