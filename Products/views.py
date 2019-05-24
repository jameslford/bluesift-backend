''' Products.views.py '''

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ProductFilter.models import DetailBuilder



@api_view(['GET'])
def product_detail(request, pk):
    detail = DetailBuilder(pk)
    response = detail.get_reponse(update=True)
    return Response(response, status=status.HTTP_200_OK)
