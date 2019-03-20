from rest_framework.decorators import (
    api_view,
    # permission_classes
    )
from .models import FinishSurface
from Products.sorter import FilterSorter


@api_view(['GET'])
def products_list(request):
    sorter = FilterSorter(request, FinishSurface)
