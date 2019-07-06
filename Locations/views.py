from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def owner_locations_list(request: HttpRequest):
    profile = request.user.get_profile()
    pass


def owner_location_detail(request, pk=None):
    user = request.user

    pass

def viewer_location_list(request, pk=None):
    pass

def viewer_location_detail(request, pk=None):
    pass
