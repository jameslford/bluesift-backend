''' views for returning customer and supplier projects/locations and
    accompanying products. supporting functions first, actual views at bottom '''

from django.conf import settings


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Profiles.models import (
    CompanyAccount,
    CompanyShippingLocation,
    SupplierProduct
    )
from Products.models import Product
from Addresses.models import Address, Zipcode

from .serializers import (
    CompanyAccountDetailSerializer,
    SVLocationSerializer,
    ShippingLocationListSerializer,
    SupplierProductUpdateSerializer
    )

''' supplier side views  '''


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def supplier_library(request):
    user = request.user
    account = CompanyAccount.objects.get_or_create(account_owner=user)[0]
    # locations = account.shipping_locations.all()
    # if not locations:
    #     locations = CompanyShippingLocation.objects.create(company_account=account)
    # locations = ShippingLocationSerializer(locations, many=True)
    # count = locations.count()
    markup = settings.MARKUP
    account = CompanyAccountDetailSerializer(account)

    return Response({
        'markup': markup,
        # 'location_count': count,
        'account': account.data,
        # 'locations': locations.data
    }, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def sv_supplier_location(request, pk=None):
    if request.method == 'POST':
        data = request.data
        company_account = data['company_account']
        loc_name = data['nickname']
        pn = data['phone_number']
        address = data['address']
        line = address['address_line_1']
        city = address['city']
        state = address['state']
        zc = address['postal_code']
        zip_code = Zipcode.objects.filter(code=zc).first()
        if not zip_code:
            return Response('invalid zip')
        address = Address.objects.create(
            address_line_1=line,
            city=city,
            state=state,
            postal_code=zip_code
        )
        company = CompanyAccount.objects.filter(id=company_account).first()
        if not company:
            return Response('invalid company')
        CompanyShippingLocation.objects.create(
            company_account=company,
            nickname=loc_name,
            phone_number=pn,
            address=address
        )
        return Response('check_it')

    if request.method == 'GET':
        location = CompanyShippingLocation.objects.filter(id=pk).first()
        user = request.user
        if not location:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if location.company_account.account_owner != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serialized = SVLocationSerializer(location)
        markup = settings.MARKUP
        return Response({
            'markup': markup,
            'location': serialized.data
            }, status=status.HTTP_200_OK)


@api_view(['PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def supplier_product(request, pk):
    user = request.user
    product = SupplierProduct.objects.get(id=pk)
    if product.supplier.company_account.account_owner != user:
        return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'PUT':
            serialized_prod = SupplierProductUpdateSerializer(data=request.data)
            if serialized_prod.is_valid():
                serialized_prod.update(instance=product, validated_data=request.data)
                return Response(status=status.HTTP_202_ACCEPTED)
            return Response(serialized_prod.errors, status=status.HTTP_402_PAYMENT_REQUIRED)


def get_company_shipping_locations(user):
    account = CompanyAccount.objects.get_or_create(account_owner=user)[0]
    locations = account.shipping_locations.all()
    if locations:
        return locations
    CompanyShippingLocation.objects.create(company_account=account)
    return CompanyShippingLocation.objects.filter(company_account=account)


def supplier_library_append(request):
    user = request.user
    locations = get_company_shipping_locations(user)
    prod_id = request.POST.get('prod_id')
    location_id = request.POST.get('proj_id', 0)
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
    suppliers = CompanyShippingLocation.objects.all()
    serialized_suppliers = ShippingLocationListSerializer(suppliers, many=True)
    return Response({'suppliers': serialized_suppliers.data})


@api_view(['GET'])
def cv_supplier_location(request, pk):
    # s_id = request.GET.get('id')
    supplier = CompanyShippingLocation.objects.get(id=pk)
    if supplier:
        serialized = SVLocationSerializer(supplier)
        return Response({'location': serialized.data}, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)