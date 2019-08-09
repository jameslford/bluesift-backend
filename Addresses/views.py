""" Address.views """

import googlemaps
from django.conf import settings
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Address


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def check_address(request: Request):
    data = request.data
    street = data.get('address_line_1', '')
    zipcode = data.get('postal_code', '')
    zipcode = zipcode.get('code', '')
    add_string = f'{street}, {zipcode}'
    gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
    response = gmaps.geocode(add_string)
    return Response(response)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_address(request: Request):
    data = request.data
    gmaps_id = data.get('gmaps_id')
    if not gmaps_id:
        return Response(None, status=status.HTTP_400_BAD_REQUEST)
    address, created = Address.objects.get_or_create_address(gmaps_id=gmaps_id)
    print(f'address was created = {created}. address gmap = {address.gmaps_id}')
    return Response(address.pk, status=status.HTTP_201_CREATED)
