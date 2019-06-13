from dataclasses import dataclass, asdict
from dataclasses import field as dfield
from typing import List
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Profiles.views import supplier_product, supplier_short_lib
from Profiles.models import CompanyShippingLocation, SupplierProduct, EmployeeProfile
from CustomerProfiles.views import customer_short_lib
from CustomerProfiles.models import CustomerProject, CustomerProduct, CustomerProfile
from Products.models import Product


@dataclass
class PLShort:
    nickname: str
    pk: int

@dataclass
class PLMedium(PLShort):
    remove: bool


@dataclass
class PLStatusList:
    pl_list: List[PLMedium]


@dataclass
class ShortLib:
    count = 0
    product_ids: List[str]
    selected_location: PLShort = None


def get_proj_or_loc(user):
    if not user.is_authenticated:
        return None
    if user.is_supplier:
        employee = EmployeeProfile.objects.filter(user=user).first()
        return employee.company_account.shipping_locations.all()
    profile = CustomerProfile.objects.get_or_create(user=user)[0]
    if not CustomerProject.objects.filter(owner=profile).exists():
        CustomerProject.objects.create(owner=user.customer_profile, nickname='First Project')
    return CustomerProject.objects.filter(owner=profile).all()


def get_user_product_model(user):
    if not user.is_authenticated:
        return None
    if user.is_suppler:
        return SupplierProduct
    return CustomerProduct


def get_pl_products(user, location) -> [str]:
    if user.is_supplier:
        return location.priced_products.values_list('product__pk', flat=True)
    return location.products.values_list('product__pk', flat=True)


def landing(request: HttpRequest):
    return HttpResponseRedirect('admin/')


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_short_lib(request):
    user = request.user
    if user.is_supplier:
        return supplier_short_lib(request)
    return customer_short_lib(request)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def pl_status_for_product(request: HttpRequest, pk):
    pl_list = PLStatusList([])
    user = request.user
    if not user:
        return Response(asdict(pl_list), status=status.HTTP_200_OK)
    product = Product.objects.get(pk=pk)
    locations = get_proj_or_loc(user)
    for location in locations:
        product_pks = get_pl_products(user, location)
        nickname = location.nickname
        pk = location.pk
        remove = product.pk in product_pks
        pl = PLMedium(nickname, pk, remove)
        pl_list.pl_list.append(pl)
    return Response(asdict(pl_list), status=status.HTTP_200_OK)

