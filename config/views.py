from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest, HttpResponseRedirect
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.shortcuts import render
from Profiles.views import (
    supplier_product,
    supplier_short_lib,
)
from CustomerProfiles.views import (
    # customer_library_append,
    customer_short_lib,
)


def landing(request: HttpRequest):
    return HttpResponseRedirect('admin/')


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# def append_lib(request):
#     user = request.user
#     if user.is_supplier:
#         # return redirect('profiles')
#         return supplier_product(request)
#     return customer_library_append(request)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_short_lib(request):
    user = request.user
    if user.is_supplier:
        return supplier_short_lib(request)
        # return Response(sup_lib, status=status.HTTP_200_OK)
    return customer_short_lib(request)
    # return Response(cus_lib, status=status.HTTP_200_OK)
