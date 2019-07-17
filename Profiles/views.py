''' views for returning customer and supplier projects/locations and
    accompanying products. supporting functions first, actual views at bottom '''
from typing import List
from dataclasses import dataclass, asdict
from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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


@api_view(['GET'])
def get_short_lib(request, pk=None):
    user = request.user
    if not user.is_authenticated:
        blank_slib = ShortLib(0, [], [])
        return Response(asdict(blank_slib), status=status.HTTP_200_OK)
    collections = user.get_collections()
    collection = collections.get(pk=pk) if pk else collections.first()
    selected_proj_loc = PLShort(collection.nickname, collection.pk)
    pl_list = collections.values('nickname', 'pk')
    product_ids = collection.products.values_list('product__pk', flat=True)
    short_lib = ShortLib(
        count=collections.count(),
        product_ids=product_ids,
        pl_short_list=pl_list,
        selected_location=selected_proj_loc
        )
    return Response(asdict(short_lib), status=status.HTTP_200_OK)


@api_view(['GET'])
def pl_status_for_product(request: HttpRequest, pk):
    pl_list = PLStatusList(pl_list=[])
    if not request.user.is_authenticated:
        return Response(asdict(pl_list), status=status.HTTP_200_OK)
    product = Product.objects.get(pk=pk)
    collections = request.user.get_collections()
    for collection in collections:
        remove = product.pk in collection.values_list('product__product__pk', flat=True)
        plmed = PLMedium(collection.nickname, collection.pk, remove)
        pl_list.pl_list.append(plmed)
    return Response(asdict(pl_list), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_library(request: HttpRequest):
    collection = request.user.get_collections()


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_profile(request: HttpRequest):

    if request.method == 'GET':
        profile = request.user.get_profile()

# from django.conf import settings
# from django.contrib.postgres.search import SearchVector
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status

# from Profiles.models import (
#     CompanyAccount,
#     EmployeeProfile,
#     CompanyShippingLocation,
#     SupplierProduct
#     )
# from Products.models import Product
# from .serializers import (
#     CompanyAccountDetailSerializer,
#     SVLocationSerializer,
#     EmployeeProfileSerializer,
#     ShippingLocationListSerializer,
#     ShippingLocationUpdateSerializer,
#     SupplierProductUpdateSerializer
#     )


# ''' supplier side views  '''


# @api_view(['GET', 'DELETE', 'PUT'])
# @permission_classes((IsAuthenticated,))
# def company_account(request):
#     user = request.user
#     employee = EmployeeProfile.objects.filter(user=user).first()
#     # only account employees can view this information
#     if not employee:
#         return Response(status=status.HTTP_403_FORBIDDEN)
#     account = employee.company_account

#     if request.method == 'GET':
#         markup = settings.MARKUP
#         account = CompanyAccountDetailSerializer(account, context={'employee': employee})
#         return Response({
#             'markup': markup,
#             'account': account.data,
#         }, status=status.HTTP_200_OK)

#     if request.method == 'DELETE':
#         # only account owner can delete company account
#         if not employee.company_account_owner:
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         account.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#     if request.method == 'PUT':
#         # only account owner and sys_admin can update company account
#         if not (employee.company_account_owner or
#                 employee.company_account_admin):
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         return Response('need to finish this')


# @api_view(['POST', 'GET', 'PUT', 'DELETE'])
# @permission_classes((IsAuthenticated,))
# def sv_supplier_location(request, pk=None):
#     user = request.user
#     employee = EmployeeProfile.objects.filter(user=user).first()
#     # only employees can access these views
#     if not employee:
#         return Response(status=status.HTTP_403_FORBIDDEN)
#     account = employee.company_account

#     if request.method == 'POST':
#         # only account owner or sys_admin can create locations
#         if not (employee.company_account_owner or
#                 employee.company_account_admin):
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         data = request.data
#         serialized_loc = ShippingLocationUpdateSerializer(data=data)
#         # if not serialized_loc.is_valid():
#         #     return Response(serialized_loc.errors, status=status.HTTP_400_BAD_REQUEST)
#         serialized_loc.create(account, data)
#         return Response('Accepted', status=status.HTTP_201_CREATED)

#     if request.method == 'GET':
#         data = request.data
#         order_by = request.GET.get('order_by', 'id')
#         search_request = request.GET.getlist('search', None)
#         location = account.shipping_locations.filter(pk=pk).select_related(
#             'address',
#             'address__postal_code',
#             'address__coordinates',
#             'company_account'
#             ).first()
#         if not location:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         serialized = SVLocationSerializer(
#             location,
#             context={
#                 'order_by': order_by,
#                 'search': search_request
#                 }
#             )
#         markup = settings.MARKUP
#         return Response({
#             'markup': markup,
#             'location': serialized.data
#             }, status=status.HTTP_200_OK)

#     if request.method == 'DELETE':
#         # only account owner or sys_admin can delete locations
#         if not (employee.company_account_owner or
#                 employee.company_account_admin):
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         location = account.shipping_locations.filter(pk=pk).first()
#         if not location:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         location.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#     if request.method == 'PUT':
#         location = account.shipping_locations.filter(pk=pk).first()
#         if not location:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         if not (employee.company_account_owner or
#                 employee.company_account_admin or
#                 employee == location.local_admin):
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         data = request.data
#         serialized_loc = ShippingLocationUpdateSerializer(data=data)
#         if not serialized_loc.is_valid():
#             return Response(serialized_loc.errors, status=status.HTTP_400_BAD_REQUEST)

#         serialized_loc.update(instance=location, validated_data=data)
#         return Response('Accepted', status=status.HTTP_202_ACCEPTED)

#     return Response('Unsupported Method', status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT', 'DELETE', 'POST'])
# @permission_classes((IsAuthenticated,))
# def supplier_product(request, proj_pk, prod_pk=None):
#     user = request.user
#     employee: EmployeeProfile = EmployeeProfile.objects.filter(user=user).first()
#     account: CompanyAccount = employee.company_account
#     location: CompanyShippingLocation = account.shipping_locations.filter(pk=proj_pk).first()
#     if not location:
#         return Response('Incorrect Proj pk', status=status.HTTP_400_BAD_REQUEST)
#     if not (
#             employee.company_account_admin or
#             employee.company_account_owner or
#             employee == location.local_admin
#             ):
#         return Response(
#             'You are not authorized to modify products for this store location',
#             status=status.HTTP_403_FORBIDDEN
#             )

#     if request.method == 'POST':
#         prod_id = request.POST.get('prod_pk', None)
#         product = Product.objects.filter(pk=prod_id).first()
#         SupplierProduct.objects.get_or_create(product=product, supplier=location)
#         return Response(status=status.HTTP_201_CREATED)

#     if request.method == 'DELETE':
#         sup_prod = location.priced_products.filter(product__pk=prod_pk).first()
#         if sup_prod:
#             sup_prod.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)

#     if request.method == 'PUT':
#         data = request.data
#         serialized_prod = SupplierProductUpdateSerializer(data=data)
#         if serialized_prod.is_valid():
#             serialized_prod.update(location=location, validated_data=data)
#             return Response(status=status.HTTP_202_ACCEPTED)

#     return Response(status=status.HTTP_400_BAD_REQUEST)



# @api_view(['GET'])
# @permission_classes((IsAuthenticated,))
# def employee_list(request):
#     user = request.user
#     user_emp_profile = EmployeeProfile.objects.filter(user=user).first()
#     if not user_emp_profile:
#         return Response('You must be an employee to view this info', status=status.HTTP_403_FORBIDDEN)
#     company = user_emp_profile.company_account
#     employees = company.employees.all()
#     serialized_emps = EmployeeProfileSerializer(employees, many=True)
#     return Response({'employess': serialized_emps.data})


# @api_view(['GET', 'PUT', 'DELETE', 'POST'])
# @permission_classes((IsAuthenticated,))
# def employee_detail(request, pk=None):
#     user = request.user
#     employee_prof = EmployeeProfile.objects.filter(user=user).first()
#     if not (employee_prof or
#             employee_prof.company_account_owner or
#             employee_prof.company_account_admin):
#         return Response('You must be an employee to view this info', status=status.HTTP_403_FORBIDDEN)

#     if request.method == 'POST':
#         email = request.data.get('email', None)
#         if not (email or
#                 '@' in email):
#             return Response('Valid email required', status=status.HTTP_400_BAD_REQUEST)
#         return Response('need to finish')

#     if not pk:
#         return Response('no employee specified')
#     employee_account = employee_prof.company_account
#     target_employee = employee_account.employees.filter(pk=pk).first()
#     if not target_employee:
#         return Response('invalid employee', status=status.HTTP_403_FORBIDDEN)

#     if request.method == 'GET':
#         serialized_employee = EmployeeProfileSerializer(target_employee)
#         return Response({'employee': serialized_employee.data}, status=status.HTTP_200_OK)

#     if request.method == 'DELETE':
#         target_employee.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#     if request.method == 'PUT':
#         return Response('need to finish')


# # customer side views 


# @api_view(['GET'])
# def supplier_list(request):
#     search_string = request.GET.get('search', None)
#     suppliers = CompanyShippingLocation.objects.all()
#     if search_string:
#         search_string = search_string.split(' ')
#         for term in search_string:
#             suppliers = suppliers.annotate(
#                 search=SearchVector(
#                     'company_account__name',
#                     'nickname',
#                     'address__address_line_1',
#                     'address__city',
#                     'address__postal_code__code'
#                 )
#             ).filter(search=term)
#     serialized_suppliers = ShippingLocationListSerializer(suppliers, many=True)
#     return Response({'suppliers': serialized_suppliers.data})

# @api_view(['GET'])
# def cv_supplier_location(request, pk):
#     supplier = CompanyShippingLocation.objects.prefetch_related(
#         'priced_products',
#         'priced_products__product',
#         'priced_products__product__manufacturer',
#     ).filter(pk=pk).first()
#     if not supplier:
#         return Response(status=status.HTTP_400_BAD_REQUEST)
#     serialized_location = SVLocationSerializer(supplier)
#     return Response({
#         'location': serialized_location.data
#         }, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def cv_supplier_location_content(request, pk):
#     from ProductFilter.models import Sorter
#     from FinishSurfaces.models import FinishSurface
#     fs_content = Sorter(FinishSurface, request=request, location_pk=pk)
#     return Response(fs_content(), status=status.HTTP_200_OK)
