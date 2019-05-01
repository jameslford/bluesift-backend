from rest_framework.decorators import (
    api_view,
    # permission_classes
    )
from rest_framework.response import Response
from rest_framework import status
from Products.sorter import FilterSorter, DetailSorter
from .serializers import SerpyFinishSurfaceMini
from .models import FinishSurface


@api_view(['GET'])
def fs_products_list(request):
    sorter = FilterSorter(request, FinishSurface, SerpyFinishSurfaceMini)
    content = sorter.return_content()
    return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
def fs_product_detail(request, pk):
    product = FinishSurface.objects.select_related(
        'material',
        'finish',
        'product',
        'product__swatch_image',
        'product__manufacturer',
        'product__room_scene',
        'product__swatch_image',
        'product__manufacturer'
    ).filter(id=pk).first()
    if not product:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    detail_sorter = DetailSorter(product)
    return Response(detail_sorter.content, status=status.HTTP_200_OK)
