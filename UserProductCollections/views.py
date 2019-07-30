""" UserProductCollections.views """

from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import BaseProject
from .serializers import RetailerLocationListSerializer, ProjectSerializer


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
    if request.user.is_supplier:
        return Response(
            RetailerLocationListSerializer(collections, many=True).data,
            status=status.HTTP_200_OK
        )
    return Response(
        ProjectSerializer(collections, many=True).data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_project(request: Request):
    """
    sole endpoint to add a project - model manager will differentiate between user and pro_user
    """

    if request.method == 'POST':
        try:
            project = BaseProject.objects.create_project(request.user, **request.data)
            return Response(status=status.HTTP_201_CREATED)
        except ValidationError as error:
            return Response(error.message, status=status.HTTP_400_BAD_REQUEST)

    return Response('Unsupported method', status=status.HTTP_405_METHOD_NOT_ALLOWED)
