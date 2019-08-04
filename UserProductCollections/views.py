""" UserProductCollections.views """

from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from config.custom_permissions import OwnerOrAdmin
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
    print('getting library = ', collections)
    if request.user.is_supplier:
        return Response(
            RetailerLocationListSerializer(collections, many=True).data,
            status=status.HTTP_200_OK
        )
    return Response(
        ProjectSerializer(collections, many=True).data,
        status=status.HTTP_200_OK
    )


@api_view(['POST', 'DELETE'])
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

    return Response('Unsupported method', status=status.HTTP_405_METHOD_NOT_ALLOWED)
