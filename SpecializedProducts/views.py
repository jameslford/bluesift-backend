from rest_framework.decorators import (
    api_view,
    # permission_classes
    )
from rest_framework.response import Response
from rest_framework import status
# from django.conf import settings
from ProductFilter.models import Sorter
# from SpecializedProduct.models import FinishSurface
from SpecializedProducts.models import FinishSurface

@api_view(['GET'])
def fs_products_list(request, update=False):
    content = Sorter(FinishSurface, request=request, update=update)
    return Response(content(), status=status.HTTP_200_OK)
