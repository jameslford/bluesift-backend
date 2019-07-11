from django.http import HttpRequest
from rest_framework.decorators import (
    api_view,
    # permission_classes
    )
from rest_framework.response import Response
from rest_framework import status
from ProductFilter.models import Sorter
from .models import ProductSubClass


@api_view(['GET'])
def products_list(request: HttpRequest, product_type: str, location_pk: int = None, update=False):
    pt = [cls for cls in ProductSubClass.__subclasses__() if cls.__name__.lower() == product_type.lower()]
    if not pt:
        return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
    content = Sorter(pt[0], request=request, location_pk=location_pk, update=update)
    return Response(content(), status=status.HTTP_200_OK)
