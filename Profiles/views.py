from django.shortcuts import render
from django.http import HttpResponse


from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Profiles.models import CompanyAccount, CompanyShippingLocation, CustomerProfile, CustomerProject, SupplierProduct
from Products.models import Product
# Create your views here.


@api_view(['GET','POST'])
@permission_classes((IsAuthenticated,))
def user_library(request):
    # products = Product.objects.all()
    user = request.user
    if request.method == 'POST':
        prod_id = request.POST.get('prod_id')
        product = Product.objects.get(id=prod_id)
        if user.is_supplier == True:
            return Response(append_supplier_location(user, product))
        else:
            return Response(append_customer_project(user, product))
    elif request.method == 'GET':
        if user.is_supplier == True:
            return Response(get_supplier_lib(user))
        else:
            return Response(get_customer_lib(user))
    else:
        return Response(status=status.HTTP_412_PRECONDITION_FAILED)


def append_supplier_location(user, product, location_id=0):
    try:
        account = user.CompanyAccount
    except (CompanyAccount.DoesNotExist):
        account = CompanyAccount.objects.create(account_owner=user)
    try:
        count = account.shipping_locations.all().count()
    except:
        CompanyShippingLocation.objects.create(company_account=account)
        count = account.shipping_locations.all().count()
    if location_id != 0:
        location = CompanyShippingLocation.objects.get(id=location_id)
        SupplierProduct.objects.create(product=product, location=location)
        return status.HTTP_201_CREATED
    elif count == 1 and location_id == 0:
        location = account.shipping_locations.first()
        SupplierProduct.objects.create(product=product, location=location)
        return status.HTTP_201_CREATED
    elif count > 1 and location_id == 0:
        return "location not specified"    
    else:
        return "user has no locations"

        


    

def append_customer_project(user, prod_id):
    pass

def get_supplier_lib(user):
    pass

def get_customer_lib(user):
    pass


    # if user.is_supplier == True:
        
    # else:
    #     try:
    #         user.CustomerProfile        
    #     except (CustomerProfile.DoesNotExist):
    #         CustomerProfile.objects.create(user=user)
        
    #     lib_products = library.products.all()
    #     serialized_products = ProductSerializer(lib_products, many=True)

    #     if request.method == 'POST':
    #         prod_id = request.POST.get('prod_id')
    #         product = products.get(id=prod_id)
    #         library.products.add(product)
    #         library.save()
    #         return Response({"library" : serialized_products.data})
    #     elif request.method == 'GET':
    #         return Response({"library" : serialized_products.data})