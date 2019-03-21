from rest_framework.decorators import (
    api_view,
    # permission_classes
    )
from .models import FinishSurface
from .serializers import SerpyFinishSurfaceMini
from Products.sorter import FilterSorter


@api_view(['GET'])
def fs_products_list(request):
    sorter = FilterSorter(request, FinishSurface)

