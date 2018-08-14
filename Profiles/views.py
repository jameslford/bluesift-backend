from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


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
from Products.serializers import ProductSerializer
from .serializers import(
                            ShippingLocationSerializer, 
                            CustomerProjectSerializer, 
                            CustomerProductSerializer, 
                            SupplierProductSerializer
                        )



@api_view(['GET','POST'])
@permission_classes((IsAuthenticated,))
def user_library(request):
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



# _________________Supplier handling_________________________________

# Supplier POST request
def append_supplier_location(user, product, location_id=0):
    locations = get_company_shipping_locations(user)
    location_count = locations.count()
    if location_id != 0:
        location = CompanyShippingLocation.objects.get(id=location_id)
        SupplierProduct.objects.create(product=product, supplier=location)
        return status.HTTP_201_CREATED
    elif location_count == 1 and location_id == 0:
        location = locations.first()
        SupplierProduct.objects.create(product=product, supplier=location)
        return status.HTTP_201_CREATED
    elif location_count > 1 and location_id == 0:
        return "location not specified"    
    else:
        return "user has no locations"




# Supplier GET request
def get_supplier_lib(user):
    locations = get_company_shipping_locations(user)
    locations_list = []
    product_id_list = []
    for location in locations:
        products_list = get_location_products(location)
        content = {
            'id': location.id,
            'nickname': location.nickname,
            'address': location.address,
            'approved_seller': location.approved_seller,
            'products': products_list[0]
        }
        locations_list.append(content)
        product_id_list.append(products_list[1])
    return {
                'locations': locations_list,
                'locations_count': len(locations_list),
                'product_ids': set(product_id_list[0])
            }




def get_location_products(location):
    product_list = []
    product_id_list = []
    supplier_products = location.priced_products.all()
    for supplier_product in supplier_products:
        product = supplier_product.product
        serialized_product = ProductSerializer(product).data
        serializer = SupplierProductSerializer().data
        # supplier product fields
        serializer['id'] = supplier_product.id
        serializer['my_price'] = supplier_product.my_price
        serializer['for_sale'] = supplier_product.for_sale
        serializer['units_available'] = supplier_product.units_available
        serializer['units_per_order'] = supplier_product.units_per_order
        serializer['price_per_unit'] = supplier_product.price_per_unit
        # product fields
        serializer['product_id'] = product.id
        serializer['product_type'] = product.product_type.material
        serializer['image'] = serialized_product['image']
        serializer['is_priced'] = product.is_priced
        serializer['lowest_price'] = product.lowest_price
        serializer['prices'] = product.prices()
        product_list.append(serializer)
        product_id_list.append(supplier_product.product.id)
    return [product_list, product_id_list]



def get_company_shipping_locations(user):
    account = CompanyAccount.objects.get_or_create(account_owner=user)[0]
    locations = account.shipping_locations.all()
    if locations:
        return locations
    else:
        CompanyShippingLocation.objects.create(company_account=account)
        return CompanyShippingLocation.objects.filter(company_account=account)[0]



# ______________Customer handling_________________________

def append_customer_project(user, product, project_id=0):
    projects = get_customer_projects(user)
    project_count = projects.count()
    if project_id != 0:
        project = CustomerProject.objects.get(id=project_id)
        CustomerProduct.objects.create(project=project, product=product)
        return status.HTTP_201_CREATED
    elif project_count == 1 and project_id == 0:
        project = projects.first()
        CustomerProduct.objects.create(project=project, product=product)
    elif project_count > 1 and project_id == 0:
         return "project not specified"    
    else:
        return "user has no project"


def get_customer_lib(user):
    profile = check_customer_profile(user)
    projects = profile.projects.all()
    projects_list = []
    product_id_list = []
    for project in projects:
        products_list = get_project_products(project)
        content = {
            'id' : project.id,
            'nickname': project.nickname,
            'address': project.address,
            'products': products_list[0]
        }
        projects_list.append(content)
        product_id_list.append(products_list[1])
    return {
            'projects': projects_list,
            'project_count': len(projects_list),
            'product_ids': set(product_id_list[0])
            }



def get_project_products(project):
    product_list = []
    product_id_list = []
    customer_products = project.products.all()
    for customer_product in customer_products:
        product = customer_product.product
        serialized_product = ProductSerializer(product).data
        serializer = CustomerProductSerializer().data
        #customer product fields
        serializer['id'] = customer_product.id
        serializer['use'] = customer_product.use
        serializer['product_id'] = serialized_product['id']
        serializer['name'] =  product.name
        serializer['image'] = serialized_product['image']
        serializer['lowest_price'] = product.lowest_price
        serializer['is_priced'] = product.is_priced
        serializer['product_type'] = product.product_type.material
        serializer['prices'] = product.prices()
        product_list.append(serializer)
        product_id_list.append(customer_product.product.id)
    return [product_list, product_id_list]


def get_customer_projects(user):
    profile = CustomerProfile.objects.get_or_create(user=user)[0]
    projects = profile.projects.all()
    if projects:
        return projects
    else:
        CustomerProject.objects.create(owner=profile)
        return CustomerProject.objects.filter(owner=profile)[0]


# def check_customer_profile(user):
#     try:
#         profile = user.user_profile
#         return profile
#     except:
#         profile = CustomerProfile.objects.create(user=user)
#         return profile


# def customer_project_count(profile):
#     try:
#         count = profile.projects.count()
#         return count
#     except:
#         CustomerProject.objects.create(owner=profile, nickname='Main Project')
#         count = profile.projects.count()
#         return count



# def check_company_account(user):
#     try:
#         account = user.company_account
#         return account
#     except:
#         CompanyAccount.objects.create(account_owner=user)
#         account = CompanyAccount
#         return account



# def supplier_location_count(account):
#     try:
#         count = account.shipping_locations.all().count()
#         return count
#     except:
#         CompanyShippingLocation.objects.create(company_account=account, nickname='Main Location')
#         count = account.shipping_locations.all().count()
#         return count

