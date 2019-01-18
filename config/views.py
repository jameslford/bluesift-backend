from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from Profiles.views import (
    supplier_library_append,
    supplier_short_lib,
)
from CustomerProfiles.views import (
    customer_library_append,
    customer_short_lib,
)


def landing(request):
    return render(request, 'index.html')


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def append_lib(request):
    user = request.user
    if user.is_supplier:
        return supplier_library_append(request)
    return customer_library_append(request)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_short_lib(request):
    user = request.user
    if user.is_supplier:
        return supplier_short_lib(request)
    return customer_short_lib(request)
