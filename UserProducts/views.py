"""
    UserProduct.views

    - generic_add
    - generic_delete
    - edit_retailer_product

"""
from django.core.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from config.custom_permissions import RetailerPermission
from .models import ProjectProduct, RetailerProduct
from .serializers import FullRetailerProductSerializer

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def generic_add(request, collection_pk=None):
    product_pk = request.POST.get('product_pk', None)
    if not product_pk:
        return Response('invalid pk', status=status.HTTP_400_BAD_REQUEST)
    if request.user.is_supplier:
        RetailerProduct.objects.add_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_201_CREATED)
    ProjectProduct.objects.add_product(request.user, product_pk, collection_pk)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def generic_delete(request, product_pk, collection_pk=None):
    if request.user.is_supplier:
        RetailerProduct.objects.delete_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_200_OK)
    ProjectProduct.objects.delete_product(request.user, product_pk, collection_pk)
    return Response(status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes((IsAuthenticated, RetailerPermission))
def edit_retailer_product(request: Request):
    data = request.data
    updates = 0
    try:
        updates = RetailerProduct.objects.update_product(request.user, **data)
    except PermissionDenied:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(f'{updates} products updated', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, RetailerPermission))
def retailer_products(request, location_pk):
    location = request.user.get_collections().get(pk=location_pk)
    products = location.products.select_related(
        'product',
        'product__manufacturer'
    ).all()
    return Response(FullRetailerProductSerializer(products, many=True).data, status=status.HTTP_200_OK)
