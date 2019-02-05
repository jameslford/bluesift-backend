''' views for returning customer and supplier projects/locations and
    accompanying products. supporting functions first, actual views at bottom '''

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.contrib.postgres.search import SearchVector
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework import status

from Profiles.models import (
    EmployeeProfile,
    CompanyShippingLocation,
    SupplierProduct
    )
from Products.models import Product
# from Addresses.models import Address, Zipcode

from .serializers import (
    CompanyAccountDetailSerializer,
    SVLocationSerializer,
    CVLocationSerializer,
    EmployeeProfileSerializer,
    ShippingLocationListSerializer,
    ShippingLocationUpdateSerializer,
    SupplierProductUpdateSerializer
    )

''' supplier side views  '''

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def location_product_search(request):
    pass



@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated,))
def company_account(request):
    user = request.user
    employee = EmployeeProfile.objects.filter(user=user).first()
    # only account employees can view this information
    if not employee:
        return Response(status=status.HTTP_403_FORBIDDEN)
    account = employee.company_account

    if request.method == 'GET':
        markup = settings.MARKUP
        account = CompanyAccountDetailSerializer(account)
        return Response({
            'markup': markup,
            'account': account.data,
        }, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        # only account owner can delete company account
        if not employee.company_account_owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == 'PUT':
        # only account owner and sys_admin can update company account
        if not (employee.company_account_owner or
                employee.company_account_admin):
                return Response(status=status.HTTP_403_FORBIDDEN)
        return Response('need to finish this')


@api_view(['POST', 'GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def sv_supplier_location(request, pk=None):
    user = request.user
    employee = EmployeeProfile.objects.filter(user=user).first()
    # only employees can access these views
    if not employee:
            return Response(status=status.HTTP_403_FORBIDDEN)
    account = employee.company_account

    if request.method == 'POST':
        # only account owner or sys_admin can create locations
        if not (employee.company_account_owner or
                employee.company_account_admin):
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = request.data
        serialized_loc = ShippingLocationUpdateSerializer(data=data)
        if not serialized_loc.is_valid():
            return Response(serialized_loc.errors, status=status.HTTP_400_BAD_REQUEST)
        serialized_loc.create(account, data)
        return Response('Accepted', status=status.HTTP_201_CREATED)

    if request.method == 'GET':
        data = request.data
        order_by = request.GET.get('order_by', 'id')
        search_request = request.GET.getlist('search', None)
        location = account.shipping_locations.filter(id=pk).first()
        if not location:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serialized = SVLocationSerializer(
            location.select_related('priced_products'),
            context={
                'order_by': order_by,
                'search': search_request
                }
            )
        markup = settings.MARKUP
        return Response({
            'markup': markup,
            'location': serialized.data
            }, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        # only account owner or sys_admin can delete locations
        if not (employee.company_account_owner or
                employee.company_account_admin):
            return Response(status=status.HTTP_403_FORBIDDEN)
        location = account.shipping_locations.filter(id=pk).first()
        if not location:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        location.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == 'PUT':
        location = account.shipping_locations.filter(id=pk).first()
        if not location:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not (employee.company_account_owner or
                employee.comapny_account_admin or
                employee == location.local_admin):
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = request.data
        serialized_loc = ShippingLocationUpdateSerializer(data)
        if not serialized_loc.is_valid():
            return Response(serialized_loc.errors, status=status.HTTP_400_BAD_REQUEST)

        serialized_loc.update(instance=location, validated_data=data)
        return Response('Accepted', status=status.HTTP_202_ACCEPTED)

@api_view(['PUT', 'DELETE', 'POST'])
@permission_classes((IsAuthenticated,))
def supplier_product(request, pk=None):
    user = request.user
    employee = EmployeeProfile.objects.filter(user=user).first()
    # only employees can access these views
    if not employee:
            return Response(status=status.HTTP_403_FORBIDDEN)

    sup_prod = None
    if pk:
        sup_prod = SupplierProduct.objects.filter(id=pk).first()
        if not sup_prod:
            return Response('invalid supplier product')
        if sup_prod.supplier.company_account != employee.company_account:
            return Response('invalid supplier product - account')
        if not (employee.company_account_owner or
                employee.company_account_admin or
                employee == sup_prod.supplier.local_admin):
            return Response(
                'You are not authorized to modify products for this store location',
                status=status.HTTP_403_FORBIDDEN
                    )

    if request.method == 'DELETE':
        sup_prod.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == 'PUT':
        data = request.data
        serialized_prod = SupplierProductUpdateSerializer(data=data)
        if serialized_prod.is_valid():
            serialized_prod.update(instance=sup_prod, validated_data=data)
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serialized_prod.errors, status=status.HTTP_402_PAYMENT_REQUIRED)

    if request.method == 'POST':
        locations = employee.company_account.shipping_locations.all()
        if not locations:
            return Response('No locations for this account', status=status.HTTP_400_BAD_REQUEST)

        location = None
        location_id = request.POST.get('proj_id', None)
        if location_id:
            location = locations.filter(id=location_id).first()
        elif locations.count() == 1:
            location = locations.first()
        if not location:
            return Response('Invalid Location', status=status.HTTP_400_BAD_REQUEST)

        product = None
        prod_id = request.POST.get('prod_id', None)
        if not prod_id:
            return Response('No product selected', status=status.HTTP_400_BAD_REQUEST)
        product = Product.objects.filter(id=prod_id).first()
        if not product:
            return Response('Invalid product', status=status.HTTP_400_BAD_REQUEST)

        if not (employee.company_account_owner or
                employee.company_account_admin or
                employee == location.local_admin):
            return Response(
                'You are not authorized to modify products for this store location',
                status=status.HTTP_403_FORBIDDEN
                    )

        SupplierProduct.objects.create(product=product, supplier=location)
        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def employee_list(request):
    user = request.user
    user_emp_profile = EmployeeProfile.objects.filter(user=user).first()
    if not user_emp_profile:
        return Response('You must be an employee to view this info', status=status.HTTP_403_FORBIDDEN)
    company = user_emp_profile.company_account
    employees = company.employees.all()
    serialized_emps = EmployeeProfileSerializer(employees, many=True)
    return Response({'employess': serialized_emps.data})


@api_view(['GET', 'PUT', 'DELETE', 'POST'])
@permission_classes((IsAuthenticated,))
def employee_detail(request, pk=None):
    user = request.user
    employee_prof = EmployeeProfile.objects.filter(user=user).first()
    if not (employee_prof or
            employee_prof.company_account_owner or
            employee_prof.company_account_admin):
        return Response('You must be an employee to view this info', status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        email = request.data.get('email', None)
        if not (email or
                '@' in email):
            return Response('Valid email required', status=status.HTTP_400_BAD_REQUEST)
        return Response('need to finish')

    if not pk:
        return Response('no employee specified')
    employee_account = employee_prof.company_account
    target_employee = employee_account.employees.filter(id=pk).first()
    if not target_employee:
        return Response('invalid employee', status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serialized_employee = EmployeeProfileSerializer(target_employee)
        return Response({'employee': serialized_employee.data}, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        target_employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == 'PUT':
        return Response('need to finish')


def supplier_short_lib(request):
    user = request.user
    employee = EmployeeProfile.objects.filter(user=user).first()
    if not employee:
        return Response('not an employee', status=status.HTTP_400_BAD_REQUEST)

    locations = employee.company_account.shipping_locations.all()
    if not locations:
        return Response('no locations', status=status.HTTP_400_BAD_REQUEST)

    location = None
    location_id = request.GET.get('proj_id', None)
    if location_id:
        location = locations.filter(id=location_id).first()
    elif locations.count() > 0:
        location = locations.first()
    else:
        return Response('Invalid Location', status=status.HTTP_400_BAD_REQUEST)

    locations_list = []
    for local in locations:
        content = {}
        content['nickname'] = local.nickname
        content['id'] = local.id
        locations_list.append(content)

    product_ids = []
    products = location.priced_products.all()
    for prod in products:
        product_ids.append(prod.product.id)

    full_content = {
        'list': locations_list,
        'count': locations.count(),
        'selected_location': {
            'nickname': location.nickname,
            'id': location.id
        },
        'product_ids': product_ids
    }
    response = {'shortLib': full_content}
    return Response(response, status=status.HTTP_200_OK)


''' customer side views '''


@api_view(['GET'])
def supplier_list(request):
    search_string = request.GET.get('search', None)
    suppliers = CompanyShippingLocation.objects.all()
    if search_string:
        search_string = search_string.split(' ')
        for term in search_string:
            suppliers = suppliers.annotate(
                    search=SearchVector(
                        'company_account__name',
                        'nickname',
                        'address__address_line_1',
                        'address__city',
                        'address__postal_code__code'
                    )
            ).filter(search=term)
    serialized_suppliers = ShippingLocationListSerializer(suppliers, many=True)
    return Response({'suppliers': serialized_suppliers.data})


@api_view(['GET'])
def cv_supplier_location(request, pk):
    # s_id = request.GET.get('id')
    supplier = CompanyShippingLocation.objects.get(id=pk)
    if supplier:
        serialized = CVLocationSerializer(supplier)
        return Response({'location': serialized.data}, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

# loc_name = data['nickname']
# pn = data['phone_number']
# address = data['address']
# line = address['address_line_1']
# city = address['city']
# state = address['state']
# zc = address['postal_code']
# zip_code = Zipcode.objects.filter(code=zc).first()
# if not zip_code:
#     return Response('invalid zip')
# address = Address.objects.create(
#     address_line_1=line,
#     city=city,
#     state=state,
#     postal_code=zip_code
#     )

# CompanyShippingLocation.objects.create(
#     company_account=account,
#     nickname=loc_name,
#     phone_number=pn,
#     address=address
#     )
# return Response('check_it')


# def get_company_shipping_locations(user):
#     account = CompanyAccount.objects.get_or_create(account_owner=user)[0]
#     locations = account.shipping_locations.all()
#     if locations:
#         return locations
#     CompanyShippingLocation.objects.create(company_account=account)
#     return CompanyShippingLocation.objects.filter(company_account=account)


# def supplier_library_append(request):
#     user = request.user
#     locations = get_company_shipping_locations(user)
#     prod_id = request.POST.get('prod_id')
#     location_id = request.POST.get('proj_id', 0)
#     product = Product.objects.get(id=prod_id)
#     count = locations.count()
#     if location_id != 0:
#         location = locations.get(id=location_id)
#         SupplierProduct.objects.create(product=product, supplier=location)
#         return Response(status=status.HTTP_201_CREATED)
#     elif count == 1:
#         location = locations.first()
#         SupplierProduct.objects.create(product=product, supplier=location)
#         return Response(status=status.HTTP_201_CREATED)
#     else:
#         return Response(status=status.HTTP_412_PRECONDITION_FAILED)
