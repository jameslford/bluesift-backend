from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from config.custom_permissions import RetailerPermission
from Products.models import Product
from Products.serializers import SerpyProduct
from .models import ProjectProduct, RetailerProduct
from .serializers import RetailerProductDetailSerializer


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
def retailer_products(request: HttpRequest, location_pk):
    location = request.user.get_collections().filter(pk=location_pk).first()
    if not location:
        return Response('Invalid project pk', status=status.HTTP_400_BAD_REQUEST)
    location_products = RetailerProduct.objects.select_related(
        'product',
        'product__manufacturer'
    ).filter(retailer=location)
    return Response(
        RetailerProductDetailSerializer(location_products, many=True).data,
        status=status.HTTP_200_OK)


# @api_view(['GET'])
# def retailer_location_products(request, product_type: str, location_pk):
#     from ProductFilter.models import Sorter
#     from Products.models import ProductSubClass
#     pt = [cls for cls in ProductSubClass.__subclasses__() if cls.__name__.lower() == product_type.lower()]
#     if not pt:
#         return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
#     fs_content = Sorter(pt, request=request, location_pk=location_pk)
#     return Response(fs_content(), status=status.HTTP_200_OK)


    # collections = request.user.get_collections()
    # if not collections:
    #     return Response('No collections object for this user', status=status.HTTP_400_BAD_REQUEST)
    # collection = collections.filter(pk=collection_pk).first() if collection_pk else collections.first()
    # if not collection:
    #     return Response('invalid collection pk')
    # user_product_type = request.user.get_user_product_type()
    # if request.method == 'POST':
    #     user_product_type.objects.create(
    #         product=
    #     )

