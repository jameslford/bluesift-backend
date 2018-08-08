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
from .serializers import ShippingLocationSerializer, CustomerProjectSerializer, CustomerProductSerializer 
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
    account = check_company_account(user)
    location_count = supplier_location_count(account)
    if location_id != 0:
        location = account.shipping_locations.get(id=location_id)
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






def append_customer_project(user, product, project_id=0):
    profile = check_customer_profile(user)
    project_count = customer_project_count(profile)
    if project_id != 0:
        project = profile.projects.get(id=project_id)
        CustomerProduct.objects.create(project=project, product=product)
        return status.HTTP_201_CREATED
    elif project_count == 1 and project_id == 0:
        project = profile.projects.first()
        CustomerProduct.objects.create(project=project, product=product)
    elif project_count > 1 and project_id == 0:
         return "project not specified"    
    else:
        return "user has no project"



def get_supplier_lib(user):
    account = check_company_account(user)
    locations = account.shipping_locations
    serialized = ShippingLocationSerializer(locations, many=True)
    return ({"locations" : serialized.data})

def get_customer_lib(user):
    profile = check_customer_profile(user)
    projects = profile.customerproject_set.all()
    projects_list = []
    for project in projects:
        products_list = get_project_products(project)
        address = project.address
        nickname = project.nickname
        content = {
            'nickname': nickname,
            'address': address,
            'products': products_list
        }
        projects_list.append(content)
    return {'projects': projects_list}


def get_project_products(project):
    product_list = []
    customer_products = project.customer_products
    for product in customer_products:
        # serializer = CustomerProductSerializer.data
        application = product.application
        product_name = product.product.name
        content = {
            'name' : product_name,
            'application' : application
        }
        product_list.append(content)
    return product_list



def check_customer_profile(user):
    try:
        profile = user.user_profile
        return profile
    except:
        profile = CustomerProfile.objects.create(user=user)
        return profile

def customer_project_count(profile):
    try:
        count = profile.projects.count()
        return count
    except:
        CustomerProject.objects.create(owner=profile, nickname='Main Project')
        count = profile.projects.count()
        return count


def check_company_account(user):
    try:
        account = user.CompanyAccount
    except (CompanyAccount.DoesNotExist):
        account = CompanyAccount.objects.create(account_owner=user)

def supplier_location_count(account):
    try:
        count = account.shipping_locations.all().count()
        return count
    except:
        CompanyShippingLocation.objects.create(company_account=account, nickname='Main Location')
        count = account.shipping_locations.all().count()
        return count





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