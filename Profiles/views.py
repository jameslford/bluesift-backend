''' views for returning customer and supplier projects/locations and
    accompanying products. supporting functions first, actual views at bottom
'''
from typing import List
from dataclasses import dataclass, asdict
from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from Products.models import Product
from Profiles.models import BaseProfile, ProEmployeeProfile
from .serializers import serialize_profile
# from .serializers import ProEmployeeProfileSerializer, RetailerEmployeeProfileSerializer, ConsumerProfileSerializer


@dataclass
class PLShort:
    nickname: str
    pk: int


@dataclass
class PLMedium(PLShort):
    remove: bool


@dataclass
class PLStatusList:
    pl_list: List[PLMedium]


@dataclass
class ShortLib:
    count: int
    product_ids: List[str]
    pl_short_list: List[PLShort]
    selected_location: PLShort = None


@api_view(['GET'])
def get_short_lib(request, pk=None):
    user = request.user
    blank_slib = ShortLib(0, [], [])
    if not user.is_authenticated:
        return Response(asdict(blank_slib), status=status.HTTP_200_OK)
    collections = user.get_collections()
    collection = collections.get(pk=pk) if pk else collections.first()
    if not collection:
        return Response(asdict(blank_slib), status=status.HTTP_200_OK)
    selected_proj_loc = PLShort(collection.nickname, collection.pk)
    pl_list = collections.values('nickname', 'pk')
    product_ids = collection.products.values_list('product__pk', flat=True)
    short_lib = ShortLib(
        count=collections.count(),
        product_ids=product_ids,
        pl_short_list=pl_list,
        selected_location=selected_proj_loc
        )
    return Response(asdict(short_lib), status=status.HTTP_200_OK)


@api_view(['GET'])
def pl_status_for_product(request: HttpRequest, pk):
    pl_list = PLStatusList(pl_list=[])
    if not request.user.is_authenticated:
        return Response(asdict(pl_list), status=status.HTTP_200_OK)
    product = Product.objects.get(pk=pk)
    collections = request.user.get_collections()
    for collection in collections:
        remove = product.pk in collection.products.values_list('product__pk', flat=True)
        plmed = PLMedium(collection.nickname, collection.pk, remove)
        pl_list.pl_list.append(plmed)
    return Response(asdict(pl_list), status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes((IsAuthenticated,))
def profile_crud(request: Request):

    if request.method == 'GET':
        return Response(serialize_profile(request.user), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        data = request.data
        BaseProfile.objects.update_profile(request.user, **data)
        return Response(serialize_profile(request.user))

    return Response('unsupported method')



@api_view(['GET'])
# @permission_classes((IsAuthenticated,))
def show_employees(request: Request, service_pk: int):
    published_employees = ProEmployeeProfile.objects.filter(company__pk=service_pk, publish=True)
    published_employees = [serialize_profile(emp) for emp in published_employees]
    if request.user.is_authenticated:
        profile: BaseProfile = request.user.get_profile()
        my_collabs = [prof.pk for prof in profile.collaborators]
        published_employees = [prof.update({'add': bool(prof['pk'] in my_collabs)}) for prof in published_employees]
    return Response(published_employees, status=status.HTTP_200_OK)



# @api_view(['GET'])
# @permission_classes((IsAuthenticated,))
# def short_collabs(request: Request, service_pk: int):
#     projects = request.user.get_collections()
#     pro_collab = Collaborator.objects.filter(collaborator__pk=service_pk).values_list('project__pk', flat=True)
#     return Response(
#         [{'nickname': proj.nickname, 'pk': proj.pk, 'remove': proj.pk in pro_collab} for proj in projects],
#         status=status.HTTP_200_OK)

        # profile = request.user.get_profile()
        # if request.user.is_pro:
        #     return Response(ProEmployeeProfileSerializer(profile).data, status=status.HTTP_200_OK)
        # if request.user.is_supplier:
        #     return Response(RetailerEmployeeProfileSerializer(profile).data, status=status.HTTP_200_OK)
        # return Response(ConsumerProfileSerializer(profile).data, status=status.HTTP_200_OK)
