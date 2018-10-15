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
from .serializers import(
    CustomerProjectSerializer,
    ShippingLocationSerializer,
    ShippingLocationDetailSerializer,
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




# # _________________Supplier handling_________________________________

# # Supplier POST request
# def append_supplier_location(user, product, location_id=0):
#     locations = get_company_shipping_locations(user)
#     location_count = locations.count()
#     if location_id != 0:
#         location = CompanyShippingLocation.objects.get(id=location_id)
#         SupplierProduct.objects.create(product=product, supplier=location)
#         return status.HTTP_201_CREATED
#     elif location_count == 1 and location_id == 0:
#         location = locations.first()
#         SupplierProduct.objects.create(product=product, supplier=location)
#         return status.HTTP_201_CREATED
#     elif location_count > 1 and location_id == 0:
#         return "location not specified"    
#     else:
#         return "user has no locations"




# # Supplier GET request
# def get_supplier_lib(user):
#     locations = get_company_shipping_locations(user)
#     locations_list = []
#     product_id_list = []
#     for location in locations:
#         products_list = get_location_products(location)
#         content = {
#             'id': location.id,
#             'nickname': location.nickname,
#             'address': location.address,
#             'approved_seller': location.approved_seller,
#             'products': products_list[0]
#         }
#         locations_list.append(content)
#         product_id_list.append(products_list[1])
#     return {
#                 'locations': locations_list,
#                 'locations_count': len(locations_list),
#                 'product_ids': set(product_id_list[0])
#             }




# def get_location_products(location):
#     product_list = []
#     product_id_list = []
#     supplier_products = location.priced_products.all()
#     for supplier_product in supplier_products:
#         product = supplier_product.product
#         serialized_product = ProductSerializer(product).data
#         serializer = SupplierProductSerializer().data
#         # supplier product fields
#         serializer['id'] = supplier_product.id
#         serializer['my_price'] = supplier_product.my_price
#         serializer['for_sale'] = supplier_product.for_sale
#         serializer['units_available'] = supplier_product.units_available
#         serializer['units_per_order'] = supplier_product.units_per_order
#         serializer['price_per_unit'] = supplier_product.price_per_unit
#         # product fields
#         serializer['product_id'] = product.id
#         serializer['product_type'] = product.product_type.material
#         serializer['image'] = serialized_product['image']
#         serializer['is_priced'] = product.is_priced
#         serializer['lowest_price'] = product.lowest_price
#         serializer['prices'] = product.prices()
#         product_list.append(serializer)
#         product_id_list.append(supplier_product.product.id)
#     return [product_list, product_id_list]



# def get_company_shipping_locations(user):
#     account = CompanyAccount.objects.get_or_create(account_owner=user)[0]
#     locations = account.shipping_locations.all()
#     if locations:
#         return locations
#     else:
#         CompanyShippingLocation.objects.create(company_account=account)
#         return CompanyShippingLocation.objects.filter(company_account=account)[0]



# # ______________Customer handling_________________________







# def get_project_products(project):
#     product_list = []
#     product_id_list = []
#     customer_products = project.products.all()
#     for customer_product in customer_products:
#         product = customer_product.product
#         serialized_product = ProductSerializer(product).data
#         serializer = CustomerProductSerializer().data
#         #customer product fields
#         serializer['id'] = customer_product.id
#         serializer['use'] = customer_product.use
#         serializer['product_id'] = serialized_product['id']
#         serializer['name'] =  product.name
#         serializer['image'] = serialized_product['image']
#         serializer['lowest_price'] = product.lowest_price
#         serializer['is_priced'] = product.is_priced
#         serializer['product_type'] = product.product_type.material
#         serializer['prices'] = product.prices()
#         product_list.append(serializer)
#         product_id_list.append(customer_product.product.id)
#     return [product_list, product_id_list]



# class CustomerLibrary(generics.RetrieveUpdateDestroyAPIView):
#     def get_queryset(self):
#         user = self.request.user
#         projects = get_customer_projects(user)
#         return projects
#     serializer_class = CustomerProjectSerializer

# def get_customer_lib(user):
#     projects = get_customer_projects(user)
#     projects_list = []
#     product_id_list = []
#     for project in projects:
#         products_list = get_project_products(project)
#         content = {
#             'id' : project.id,
#             'nickname': project.nickname,
#             'address': project.address,
#             'products': products_list[0]
#         }
#         projects_list.append(content)
#         product_id_list.append(products_list[1])
#     return {
#             'projects': projects_list,
#             'project_count': len(projects_list),
#             'product_ids': set(product_id_list[0])
#             }


# def get_project_products(project):
#     product_list = []
#     product_id_list = []
#     customer_products = project.products.all()
#     for customer_product in customer_products:
#         product = customer_product.product
#         serialized_product = ProductSerializer(product).data
#         serializer = CustomerProductSerializer().data
#         #customer product fields
#         serializer['id'] = customer_product.id
#         serializer['use'] = customer_product.use
#         serializer['product_id'] = serialized_product['id']
#         serializer['name'] =  product.name
#         serializer['image'] = serialized_product['image']
#         serializer['lowest_price'] = product.lowest_price
#         serializer['is_priced'] = product.is_priced
#         serializer['product_type'] = product.product_type.material
#         serializer['prices'] = product.prices()
#         product_list.append(serializer)
#         product_id_list.append(customer_product.product.id)
#     return [product_list, product_id_list]




# def user_library(request):
#     user = request.user
#     if request.method == 'POST':
#         prod_id = request.POST.get('prod_id')
#         product = Product.objects.get(id=prod_id)
#         if user.is_supplier == True:
#             return Response(append_supplier_location(user, product))
#         else:
#             return Response(append_customer_project(user, product))
#     elif request.method == 'GET':
#         if user.is_supplier == True:
#             return Response(get_supplier_lib(user))
#         else:
#             return Response(get_customer_lib(user))
#     else:
#         return Response(status=status.HTTP_412_PRECONDITION_FAILED)
