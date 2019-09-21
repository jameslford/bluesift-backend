""" UserProductCollections.views """

from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from config.custom_permissions import OwnerOrAdmin, RetailerPermission
from Products.models import ProductSubClass, Product
from Products.serializers import serialize_product
from .models import BaseProject, RetailerLocation
from .serializers import RetailerLocationListSerializer, ProjectSerializer, RetailerLocationDetailSerializer


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_library(request: Request):
    """
    returns projects or retail_locations that apply to user.

    If user.is_supplier will return all locations that apply to the users company.

    If user.is_pro or regular user, will return all projects that the user owns, or
    will return projects that the user is included on as colloborator - which is noted
    """
    collections = request.user.get_collections()
    user = request.user
    if user.is_supplier:
        return Response(
            RetailerLocationListSerializer(collections, many=True).data,
            status=status.HTTP_200_OK
        )
    # profile = user.get_profile()
    # group = user.get_group()
    # collaborations = None
    # if user.is_pro:
    #     collaborations = BaseProject.subclasses.filter(pro_collaborator=profile).select_subclasses()
    # else:
    #     collaborations = BaseProject.subclasses.filter(collaborators=profile).select_subclasses()
    # profile = user.get_profile()
    content = {
        'my_projects': ProjectSerializer(collections, many=True).data,
        # 'collaborations': ProjectSerializer(group.collaborations, many=True).data
    }
    return Response(
        content,
        status=status.HTTP_200_OK
    )


@api_view(['POST', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated, OwnerOrAdmin))
def crud_project(request: Request, project_pk=None):
    """
    sole endpoint to add a project - model manager will differentiate between user and pro_user
    """

    if request.method == 'POST':
        try:
            project = BaseProject.objects.create_project(request.user, **request.data)
            return Response(status=status.HTTP_201_CREATED)
        except ValidationError as error:
            return Response(error.messages[1], status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        project = request.user.get_collections().filter(pk=project_pk).first()
        if not project:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        project.delete()
        return Response(status=status.HTTP_200_OK)

    if request.method == 'PUT':
        user = request.user
        data = request.data
        project = BaseProject.objects.update_project(user, **data)
        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    return Response('Unsupported method', status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated, RetailerPermission))
def crud_location(request: Request):
    """
    create, update, delete endpoint for RetailerLocation objects
    """
    user = request.user
    if request.method == 'POST':
        data = request.data
        RetailerLocation.objects.create_location(user, **data)
        return Response(status=status.HTTP_201_CREATED)

    if request.method == 'PUT':
        data = request.data
        location = RetailerLocation.objects.update_location(user, **data)
        return Response(RetailerLocationListSerializer(location).data, status=status.HTTP_200_OK)

    return Response('unsupported method', status=status.HTTP_405_METHOD_NOT_ALLOWED)




@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def project_detail(request: Request, project_pk):
    pass

@api_view(['GET'])
@permission_classes((IsAuthenticated, RetailerPermission))
def location_detail(request: Request, location_pk):
    pass


# @api_view(['GET'])
# @permission_classes((IsAuthenticated,))
# def get_project_products(request: HttpRequest, project_pk):
#     project_exist = request.user.get_collections().filter(pk=project_pk).exists()
#     if not project_exist:
#         return Response('Invalid project pk', status=status.HTTP_400_BAD_REQUEST)
#     project_products = ProjectProduct.objects.select_related(
#         ).filter(project__pk=project_pk).values_list('product__pk', flat=True)
#     products = Product.subclasses.select_related('manufacturer').filter(pk__in=project_products).select_subclasses()
#     res = []
#     for kls in ProductSubClass.__subclasses__():
#         kls_res = {
#             'name': kls.__name__,
#             'products': [serialize_product(product) for product in products if type(product) == kls]
#             }
#         res.append(kls_res)
#     return Response(res, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes((IsAuthenticated, RetailerPermission))
# def retailer_products(request: Request, location_pk, product_type):
#     prod_type = ProductSubClass().return_sub(product_type)
#     location = request.user.get_collections().filter(pk=location_pk).first().pk
#     prods = prod_type.objects.all().values('pk')
#     location_products = RetailerProduct.objects.select_related(
#         'product',
#         'product__manufacturer'
#         ).filter(product__pk__in=prods, retailer__pk=location)
#     return Response(
#         FullRetailerProductSerializer(location_products, many=True).data,
#         status=status.HTTP_200_OK)
