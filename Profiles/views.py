''' views for returning customer and supplier projects/locations and 
    accompanying products. supporting functions first, actual views at bottom '''

from django.shortcuts import render
from django.http import HttpResponse


from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Profiles.models import( 
    CompanyAccount,
    CompanyShippingLocation,
    CustomerProduct,
    CustomerProfile,
    CustomerProject,
    SupplierProduct
    )
from Products.models import Product
from Addresses.models import Address
from .serializers import(
    CustomerProjectSerializer,
    ShippingLocationSerializer,
    ShippingLocationDetailSerializer,
    ShippingLocationUpdateSerializer
    )

def get_customer_projects(user):
    profile = CustomerProfile.objects.get_or_create(user=user)[0]
    projects = profile.projects.all()
    if projects:
        return projects
    else:
        CustomerProject.objects.create(owner=profile)
        return CustomerProject.objects.filter(owner=profile)


def get_company_shipping_locations(user):
    account = CompanyAccount.objects.get_or_create(account_owner=user)[0]
    locations = account.shipping_locations.all()
    if locations:
        return locations
    else:
        CompanyShippingLocation.objects.create(company_account=account)
        return CompanyShippingLocation.objects.filter(company_account=account)


def customer_library_append(request):
    user = request.user
    projects = get_customer_projects(user)
    prod_id = request.POST.get('prod_id')
    project_id = request.POST.get('proj_id', 0)
    product = Product.objects.get(id=prod_id)
    project_count = projects.count()
    if project_id != 0:
        project = projects.get(id=project_id)
        CustomerProduct.objects.create(project=project, product=product)
        return Response(status=status.HTTP_201_CREATED)
    elif project_count == 1:
        project = projects.first()
        CustomerProduct.objects.create(project=project, product=product)
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_412_PRECONDITION_FAILED)

def supplier_library_append(request):
    user = request.user
    locations = get_company_shipping_locations(user)
    prod_id = request.POST.get('prod_id')
    location_id = request.POST.get('location_id', 0)
    product = Product.objects.get(id=prod_id)
    count = locations.count()
    if location_id != 0:
        location = locations.get(id=location_id)
        SupplierProduct.objects.create(product=product, supplier=location)
        return Response(status=status.HTTP_201_CREATED)
    elif count == 1:
        location = locations.first()
        SupplierProduct.objects.create(product=product, supplier=location)
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_412_PRECONDITION_FAILED)


def customer_short_lib(request):
    user = request.user
    proj_id = request.GET.get('proj_id')
    projects = get_customer_projects(user)
    project = projects.first()
    projects_list = []
    product_ids = []
    if proj_id:
        project = projects.get(id=proj_id)
    selected_project = {'id':project.id, 'nickname': project.nickname}
    for proj in projects:
        content = {}
        content['nickname'] = proj.nickname
        content['id'] = proj.id
        projects_list.append(content)
    products = project.products.all()
    for prod in products:
        product_ids.append(prod.product.id)
    full_content = {
        'list': projects_list,
        'count': projects.count(),
        'selected_project': selected_project,
        'product_ids': product_ids
    }
    response = {'shortLib': full_content}
    return Response(response, status=status.HTTP_200_OK)


def supplier_short_lib(request):
    user = request.user
    location_id = request.GET.get('proj_id')
    locations = get_company_shipping_locations(user)
    location = locations.first()
    locations_list = []
    product_ids = []
    if location_id:
        location = locations.get(id=location_id)
    for local in locations:
        content = {}
        content['nickname'] = local.nickname
        content['id'] = local.id
        locations_list.append(content)
    products = location.priced_products.all()
    for prod in products:
        product_ids.append(prod.product.id)
    full_content = {
        'list': locations_list,
        'count': locations.count(),
        'product_ids': product_ids
    }
    response = {'shortLib': full_content}
    return Response(response, status=status.HTTP_200_OK)


def customer_library(request):
    user = request.user
    projects = get_customer_projects(user)
    serialized_projs = CustomerProjectSerializer(projects, many=True)
    return Response(serialized_projs.data, status=status.HTTP_200_OK)


def supplier_library(request):
    user = request.user
    locations = get_company_shipping_locations(user)
    serialized_locs = ShippingLocationDetailSerializer(locations, many=True)
    return Response({'locations': serialized_locs.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def append_lib(request):
    user = request.user
    if user.is_supplier:
        return supplier_library_append(request)
    else:
        return customer_library_append(request)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_short_lib(request):
    user = request.user
    if user.is_supplier:
        return supplier_short_lib(request)
    else:
        return customer_short_lib(request)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_lib(request):
    user = request.user
    if user.is_supplier:
        return supplier_library(request)
    else:
        return customer_library(request)


@api_view(['GET'])
def supplier_list(request):
    suppliers = CompanyShippingLocation.objects.all()
    serialized_suppliers = ShippingLocationSerializer(suppliers, many=True)
    return Response({'suppliers': serialized_suppliers.data})

@api_view(['GET'])
def supplier_detail(request, pk):
    # s_id = request.GET.get('id')
    supplier = CompanyShippingLocation.objects.get(id=pk)
    if supplier:
        serialized = ShippingLocationDetailSerializer(supplier)
        return Response({'location': serialized.data}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_supplier_location(request):
    # serialized_loc = ShippingLocationUpdateSerializer(data=request.data)
    # if serialized_loc.is_valid():
        serialized_loc = request.data
        company_account = serialized_loc['company_account']
        phone = serialized_loc['phone_number']
        nickname = serialized_loc['nickname']
        address = serialized_loc['address']
        street = address['address_line_1']
        city = address['city']
        state = address['state']
        postal_code = address['postal_code']
        new_add = Address.objects.create(address_line_1=street, city=city, state=state, postal_code=postal_code)
        if new_add:
            new_loc = CompanyShippingLocation.objects.create(company_account=company_account, phone_number=phone, nickname=nickname, address=address)
            if new_loc:
                return Response('Done!', status=status.HTTP_201_CREATED)
            else:
                return Response('no new loc', status=status.HTTP_412_PRECONDITION_FAILED)
        else:
            return Response('no new add', status=status.HTTP_300_MULTIPLE_CHOICES)

    # else:
    #     return Response(serialized_loc.errors)
