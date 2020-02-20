''' views for returning customer and supplier projects/locations and
    accompanying products. supporting functions first, actual views at bottom
'''
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
# from config.serializers import serialize_profile
from Products.serializers import serialize_product
from .models import BaseProfile, LibraryProduct
from .serializers import serialize_profile



@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes((IsAuthenticated,))
def profile_crud(request: Request):

    if request.method == 'GET':
        return Response(serialize_profile(request.user.get_profile()), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        data = request.data
        BaseProfile.objects.update_profile(request.user, **data)
        return Response(serialize_profile(request.user.get_profile()))

    if request.method == 'POST':
        pass

    if request.method == 'DELETE':
        pass

    return Response('unsupported method')


@api_view(['GET', 'PUT' 'POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def collaborators(request: Request, pk=None):

    if request.method == 'GET':
        profile = BaseProfile.subclasses.select_related('consumerprofile', 'supplieremployeeprofile').get_subclass(user=request.user)
        res = [serialize_profile(col) for col in profile.collaborators.all()]
        return Response(res, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        pass

    if request.method == 'POST':
        pass

    if request.method == 'DELETE':
        pass

    return Response('unsupported method')


@api_view(['GET'])
def show_employees(request: Request, service_pk: int):
    published_employees = BaseProfile.subclasses.filter(company__pk=service_pk, publish=True).select_subclasses()
    published_employees = [serialize_profile(emp) for emp in published_employees]
    if request.user.is_authenticated:
        profile: BaseProfile = request.user.get_profile()
        my_collabs = [prof.pk for prof in profile.collaborators]
        published_employees = [prof.update({'add': bool(prof['pk'] in my_collabs)}) for prof in published_employees]
    return Response(published_employees, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def palette(request):
    profile = request.user.profile
    products = LibraryProduct.objects.select_related('product').filter(owner=profile)
    res = []
    for prod in products:
        pdict = serialize_product(prod.product)
        pro_dict = {'projects': prod.projects.values('project__pk', 'project__nickname').distinct()}
        pdict.update(pro_dict)
        pdict['pk'] = prod.pk
        pdict['project_pk'] = prod.product.pk
        res.append(pdict)
    return Response(res, status=status.HTTP_200_OK)
