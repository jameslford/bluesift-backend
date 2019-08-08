"""
    UserProduct.views

    - generic_add
    - generic_delete
    - get_project_products
    - retailer_products

"""
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from config.custom_permissions import RetailerPermission
from Products.models import Product
from Products.serializers import SerpyProduct
from .models import ProjectProduct, RetailerProduct
from .serializers import FullRetailerProductSerializer


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def generic_add(request, collection_pk=None):
    product_pk = request.POST.get('product_pk', None)
    if not product_pk:
        return Response('invalid pk', status=status.HTTP_400_BAD_REQUEST)
    product = Product.objects.filter(pk=product_pk).first()
    if request.user.is_supplier:
        RetailerProduct.objects.add_product(request.user, product, collection_pk)
        return Response(status=status.HTTP_201_CREATED)
    ProjectProduct.objects.add_product(request.user, product, collection_pk)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def generic_delete(request, product_pk, collection_pk=None):
    product = Product.objects.get(pk=product_pk)
    if request.user.is_supplier:
        RetailerProduct.objects.delete_product(request.user, product, collection_pk)
        return Response(status=status.HTTP_200_OK)
    ProjectProduct.objects.delete_product(request.user, product, collection_pk)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_project_products(request: HttpRequest, project_pk):
    project_exist = request.user.get_collections().filter(pk=project_pk).exists()
    if not project_exist:
        return Response('Invalid project pk', status=status.HTTP_400_BAD_REQUEST)
    project_products = ProjectProduct.objects.select_related(
        'product',
        'product__manufacturer'
        ).filter(project__pk=project_pk)
    products = [project_product.product for project_product in project_products]
    return Response(SerpyProduct(products, many=True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, RetailerPermission))
def retailer_products(request: Request, location_pk, product_type):
    from Products.models import ProductSubClass
    prod_type = ProductSubClass().return_sub(product_type)
    location = request.user.get_collections().filter(pk=location_pk).first().pk
    prods = prod_type.objects.all().values('pk')
    location_products = RetailerProduct.objects.select_related(
        'product',
        'product__manufacturer'
        ).filter(product__pk__in=prods, retailer__pk=location)
    return Response(
        FullRetailerProductSerializer(location_products, many=True).data,
        status=status.HTTP_200_OK)


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
