from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def retailer_location_products(request, product_type: str, location_pk):
    from ProductFilter.models import Sorter
    from Products.models import ProductSubClass
    pt = [cls for cls in ProductSubClass.__subclasses__() if cls.__name__.lower() == product_type.lower()]
    if not pt:
        return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
    fs_content = Sorter(pt, request=request, location_pk=location_pk)
    return Response(fs_content(), status=status.HTTP_200_OK)
