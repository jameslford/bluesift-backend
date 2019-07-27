from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RetailerLocationListSerializer, ProjectSerializer
# from UserProducts.models import RetailerProduct
# from Products.models import Product, ProductSubClass
# from .models import RetailerLocation


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_library(request: HttpRequest):
    collection = request.user.get_collections()
    if request.user.is_supplier:
        return Response(
            RetailerLocationListSerializer(collection, many=True).data,
            status=status.HTTP_200_OK
        )
    return Response(
        ProjectSerializer(collection, many=True).data,
        status=status.HTTP_200_OK
    )
