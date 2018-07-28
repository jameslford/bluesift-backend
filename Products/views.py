# Products.views.py

from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import( 
                        ProductSerializer, 
                        ProductTypeSerializer, 
                        ApplicationAreaSerializer, 
                        ManufacturerSerializer
                        )

from .models import(
                    Product, 
                    Application, 
                    Manufacturer, 
                    ProductType
                    )



@api_view(['GET'])
def product_list(request):

    # parse request
    is_priced = request.GET.get('is_priced', 'False')
    product_type = request.GET.get('product_type', '0')
    application_type = request.GET.get('application_type', '0')
    manufacturer = request.GET.get('manufacturer', 'All')

    # structure filter objects
    filter_content = {
        "is_priced" : is_priced,
        "product_type" : product_type,
        "application_type" : application_type,
        "manufacturer" : manufacturer,
    }

    # filter products
    pTyped_products = parse_pt(product_type)
    aTyped_products = parse_at(application_type, pTyped_products)
    mTyped_products = parse_manufacturer(manufacturer, aTyped_products)
    filtered_products = parse_priced(is_priced, mTyped_products)
    products_serialized = ProductSerializer(filtered_products, many=True)

    # filter application types
    application_types = Application.objects.all()
    # app_types_serialized = ApplicationAreaSerializer(application_types, many=True)
    # active_ats = active_at(filtered_products)
    refined_ats = app_type_enabler(ApplicationAreaSerializer, application_types, filtered_products, 'application')

    # filter manufacturers
    manufacturers = Manufacturer.objects.all()
    refined_manu = app_type_enabler(ManufacturerSerializer, manufacturers, filtered_products, 'manufacturer')
    #manufacturers_serialized = ManufacturerSerializer(manufacturers, many=True)

    # filter product types
    product_types = ProductType.objects.all()
    # prod_types_seriallized = ProductTypeSerializer(product_types, many=True)
    # active_pts = active_pt(filtered_products)
    refined_pts = app_type_enabler(ProductTypeSerializer, product_types, filtered_products, 'product')

    



    return Response({
                    "filter" : filter_content,
                    "application_types": refined_ats,
                    #"product_types": refined_pts.data,
                    "manufacturers": refined_manu,
                    "products": products_serialized.data
                    })
    



def parse_pt(product_type):
    products = Product.objects.all()
    if product_type == '0':
        return products
    else:
        return products.filter(product_type=product_type)

def parse_at(application_type, products):
    if application_type == '0':
        return products
    else:
        return products.filter(application=application_type)

def parse_manufacturer(manufacturer, products):
    if manufacturer == 'All':
        return products
    else:
        return products.filter(manufacturer=manufacturer)


def parse_priced(is_priced, products):
    if is_priced == 'true':   
        return products.filter(is_priced=True)
        # prods = []
        # for product in products:
        #     if product.is_priced() == True:
        #         prods.append(product)
                # return prods
    else:
        return products


def active_at(products):
    if products:
        actives = []
        for product in products:
            ats = product.application.all()
            for at in ats:
                actives.append(at.id)
        active = set(actives)
        return active
    else:
        return


def active_pt(products):
    if products:
        actives = []
        for product in products:
            if product.product_type:
                pt = product.product_type
                actives.append(pt.id)
        active = set(actives)
        return active
    else:
        return


# def app_type_enabler(active_ids, serialized_app_types):
#     for app_type in serialized_app_types.data:
#         if app_type['id'] in active_ids:
#             app_type['enabled'] = True
#     return serialized_app_types



def app_type_enabler(serializer, objects, products, argument):
    serialized_types = []
    for item in objects:
        count = get_argument(item, products, argument)
        # ATcount = products.filter(argument=item).count()
        at_serialized = serializer(item).data
        at_serialized['count'] = count
        if count > 0:
            at_serialized['enabled'] = True
        serialized_types.append(at_serialized)
    return serialized_types

def get_argument(item, products, argument):
    if argument == 'application':
        return products.filter(application=item).count()
    elif argument == 'manufacturer':
        return products.filter(manufacturer=item).count()
    elif argument == 'product':
        return products.filter(product_type=item).count()









@api_view(['GET'])
def get_product(request, pk):
    product = Product.objects.get(id=pk)
    serialized_product = ProductSerializer(product)
    return Response({'product': serialized_product.data})


