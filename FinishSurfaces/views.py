from rest_framework.decorators import (
    api_view,
    # permission_classes
    )
from .models import FinishSurface
from rest_framework.response import Response
from rest_framework import status
from .serializers import SerpyFinishSurfaceMini, FinishSurfaceMini
from Products.sorter import FilterSorter


@api_view(['GET'])
def fs_products_list(request):
    sorter = FilterSorter(request, FinishSurface, SerpyFinishSurfaceMini)
    content = sorter.return_content()
    return Response(content, status=status.HTTP_200_OK)
