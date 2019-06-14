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
    count: int
    product_ids: List[str]
    pl_short_list: List[PLShort]
    selected_location: PLShort = None


def get_proj_or_loc(user):
    if user.is_supplier:
        employee = EmployeeProfile.objects.filter(user=user).first()
        return employee.company_account.shipping_locations.all()
    if not CustomerProject.objects.filter(owner=user.customer_profile).exists():
        CustomerProject.objects.create(owner=user.customer_profile, nickname='First Project')
    return CustomerProject.objects.filter(owner=user.customer_profile).all()


def get_user_product_model(user):
    if user.is_suppler:
        return SupplierProduct
    return CustomerProduct


def get_pl_products(user, location) -> [str]:
    if user.is_supplier:
        return location.priced_products.values_list('product__pk', flat=True)
    return location.products.values_list('product__pk', flat=True)


def locations_list(locations) -> List[PLShort]:
    pl_list = []
    for location in locations:
        nickname = location.nickname
        pk = location.pk
        pl_list.append(PLShort(nickname, pk))
    return pl_list


def landing(request: HttpRequest):
    return HttpResponseRedirect('admin/')


@api_view(['GET'])
# @permission_classes((IsAuthenticated,))
def get_short_lib(request, pk=None):
    user = request.user
    if not user.is_authenticated:
        return None
    locations = get_proj_or_loc(user)
    location = locations.first()
    if pk:
        location = locations.get(pk=pk)
    selected_proj_loc = PLShort(location.nickname, location.pk)
    pl_list = locations_list(locations)
    products_ids = get_pl_products(user, location)
    short_lib = ShortLib(
        count=locations.count(),
        product_ids=products_ids,
        pl_short_list=pl_list,
        selected_location=selected_proj_loc
        )
    return Response(asdict(short_lib), status=status.HTTP_200_OK)


@api_view(['GET'])
# @permission_classes((IsAuthenticated,))
def pl_status_for_product(request: HttpRequest, pk):
    pl_list = PLStatusList(pl_list=[])
    user = request.user
    if not user.is_authenticated:
        return Response(asdict(pl_list), status=status.HTTP_200_OK)
    product = Product.objects.get(pk=pk)
    locations = get_proj_or_loc(user)
    locs = locations_list(locations)
    for loc in locs:
        location = locations.get(pk=loc.pk)
        product_pks = get_pl_products(user, location)
        remove = product.pk in product_pks
        plmed = PLMedium(loc.nickname, loc.pk, remove)
        pl_list.pl_list.append(plmed)
    return Response(asdict(pl_list), status=status.HTTP_200_OK)
