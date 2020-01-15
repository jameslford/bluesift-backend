''' views for returning customer and supplier projects/locations and
    accompanying products. supporting functions first, actual views at bottom
'''
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from Profiles.models import BaseProfile
from config.serializers import ProfileSerializer


@api_view(['GET', 'PUT'])
@permission_classes((IsAuthenticated,))
def profile_crud(request: Request):

    if request.method == 'GET':
        return Response(ProfileSerializer(request.user).data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        data = request.data
        BaseProfile.objects.update_profile(request.user, **data)
        return Response(ProfileSerializer(request.user).data)

    return Response('unsupported method')


@api_view(['GET'])
def show_employees(request: Request, service_pk: int):
    published_employees = BaseProfile.subclasses.filter(company__pk=service_pk, publish=True).select_subclasses()
    published_employees = [ProfileSerializer(emp).data for emp in published_employees]
    if request.user.is_authenticated:
        profile: BaseProfile = request.user.get_profile()
        my_collabs = [prof.pk for prof in profile.collaborators]
        published_employees = [prof.update({'add': bool(prof['pk'] in my_collabs)}) for prof in published_employees]
    return Response(published_employees, status=status.HTTP_200_OK)
