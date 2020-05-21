""" Address.views """

import googlemaps
from django.conf import settings
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from Profiles.models import BaseProfile
from .serializers import serialize_zipcode
from .models import Address, Zipcode


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def check_address(request: Request):
    data = request.data
    street = data.get("address_line_1", "")
    zipcode = data.get("postal_code", "")
    zipcode = zipcode.get("code", "")
    add_string = f"{street}, {zipcode}"
    gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
    response = gmaps.geocode(add_string)
    return Response(response)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def add_address(request: Request):
    data = request.data
    gmaps_id = data.get("gmaps_id")
    if not gmaps_id:
        return Response(None, status=status.HTTP_400_BAD_REQUEST)
    address, created = Address.objects.get_or_create_address(gmaps_id=gmaps_id)
    print(f"address was created = {created}. address gmap = {address.gmaps_id}")
    return Response(address.pk, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_zipcode(request):
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    profile: BaseProfile = None
    if request.user and request.user.is_authenticated:
        profile = request.user.get_profile()
    gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
    response = gmaps.reverse_geocode((float(lat), float(lng)))
    comps = response[0]["address_components"]
    res = [comp for comp in comps if "postal_code" in comp.get("types", [])]
    if res:
        code = res[0].get("long_name", None)
        zipc = Zipcode.objects.get(code=code)
        if zipc:
            if profile:
                profile.current_zipcode = zipc
                profile.save()
            return Response(serialize_zipcode(zipc), status=status.HTTP_200_OK)
    return Response(None, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def set_zipcode(request, zipcode):
    zipc = Zipcode.objects.get(code=zipcode)
    if request.user and request.user.is_authenticated:
        profile = request.user.get_profile()
        profile.current_zipcode = zipc
        profile.save()
    return Response(serialize_zipcode(zipc), status=status.HTTP_200_OK)
