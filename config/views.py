import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from Groups.models import ServiceType
from Products.models import ProductSubClass


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s1.replace('_', '-')


@api_view(['GET'])
def get_header_list(request):
    pro_types = list(ServiceType.objects.values_list('label', flat=True))
    departments = [convert(cls.__name__) for cls in ProductSubClass.__subclasses__()]
    print(f'departments={sorted(departments)}')
    return Response({
        'pros': sorted(pro_types),
        'departments': sorted(departments)
    })









# from dataclasses import dataclass, asdict
# from typing import List
# from django.http import HttpRequest, HttpResponseRedirect
# from rest_framework import status
# from Profiles.models import SupplierProduct, EmployeeProfile
# from CustomerProfiles.models import CustomerProject, CustomerProduct
# from Products.models import Product


# @dataclass
# class PLShort:
#     nickname: str
#     pk: int


# @dataclass
# class PLMedium(PLShort):
#     remove: bool


# @dataclass
# class PLStatusList:
#     pl_list: List[PLMedium]


# @dataclass
# class ShortLib:
#     count: int
#     product_ids: List[str]
#     pl_short_list: List[PLShort]
#     selected_location: PLShort = None


# def get_proj_or_loc(user):
#     if user.is_supplier:
#         employee = EmployeeProfile.objects.filter(user=user).first()
#         return employee.company_account.shipping_locations.all()
#     if not CustomerProject.objects.filter(owner=user.customer_profile).exists():
#         CustomerProject.objects.create(owner=user.customer_profile, nickname='First Project')
#     return CustomerProject.objects.filter(owner=user.customer_profile).all()


# def get_user_product_model(user):
#     if user.is_suppler:
#         return SupplierProduct
#     return CustomerProduct


# def get_pl_products(user, location) -> [str]:
#     if user.is_supplier:
#         return location.priced_products.values_list('product__pk', flat=True)
#     return location.products.values_list('product__pk', flat=True)


# def locations_list(locations) -> List[PLShort]:
#     pl_list = []
#     for location in locations:
#         nickname = location.nickname
#         pk = location.pk
#         pl_list.append(PLShort(nickname, pk))
#     return pl_list


# def landing(request: HttpRequest):
#     return HttpResponseRedirect('admin/')


# @api_view(['GET'])
# def get_short_lib(request, pk=None):
#     user = request.user
#     if not user.is_authenticated:
#         blank_slib = ShortLib(0, [], [])
#         return Response(asdict(blank_slib), status=status.HTTP_200_OK)
#     locations = get_proj_or_loc(user)
#     location = locations.first()
#     if pk:
#         location = locations.get(pk=pk)
#     selected_proj_loc = PLShort(location.nickname, location.pk)
#     pl_list = locations_list(locations)
#     products_ids = get_pl_products(user, location)
#     short_lib = ShortLib(
#         count=locations.count(),
#         product_ids=products_ids,
#         pl_short_list=pl_list,
#         selected_location=selected_proj_loc
#         )
#     return Response(asdict(short_lib), status=status.HTTP_200_OK)


# @api_view(['GET'])
# def pl_status_for_product(request: HttpRequest, pk):
#     pl_list = PLStatusList(pl_list=[])
#     user = request.user
#     if not user.is_authenticated:
#         return Response(asdict(pl_list), status=status.HTTP_200_OK)
#     product = Product.objects.get(pk=pk)
#     locations = get_proj_or_loc(user)
#     locs = locations_list(locations)
#     for loc in locs:
#         location = locations.get(pk=loc.pk)
#         product_pks = get_pl_products(user, location)
#         remove = product.pk in product_pks
#         plmed = PLMedium(loc.nickname, loc.pk, remove)
#         pl_list.pl_list.append(plmed)
#     return Response(asdict(pl_list), status=status.HTTP_200_OK)
