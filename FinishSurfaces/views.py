from rest_framework.decorators import (
    api_view,
    # permission_classes
    )
from rest_framework.response import Response
from rest_framework import status
# from django.conf import settings
from ProductFilter.models import Sorter
from .models import FinishSurface


@api_view(['GET'])
def fs_products_list(request, update=False):
    prod_filter = Sorter(FinishSurface.objects.all(), request=request, update=update)
    content = prod_filter.get_repsonse()
    return Response(content, status=status.HTTP_200_OK)
