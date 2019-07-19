from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from UserProducts.models import RetailerProduct
from Products.models import Product, ProductSubClass
from .serializers import AllRetailerLocationSerializer, ProjectSerializer
# from .models import RetailerLocation


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_library(request: HttpRequest):
    collection = request.user.get_collections()
    if request.user.is_supplier:
        return Response(
            AllRetailerLocationSerializer(collection, many=True).data,
            status=status.HTTP_200_OK
        )
    return Response(
        ProjectSerializer(collection, many=True).data,
        status=status.HTTP_200_OK
    )


# def owner_locations_list(request: HttpRequest):
#     group = request.user.get_group()


#     pass


# def owner_location_detail(request, pk=None):
#     user = request.user

#     pass

# def viewer_location_list(request, pk=None):
#     pass

# def viewer_location_detail(request, pk=None):
#     pass
