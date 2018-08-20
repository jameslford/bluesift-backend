# Products.views.py

from django.shortcuts import render
from django.core.serializers import serialize
from django.db.models import Q

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
                    Build,
                    Material, 
                    Manufacturer, 
                    )



@api_view(['GET'])
def product_list(request):

    # parse request
    for_sale = request.GET.get('for_sale', 'False')
    product_type = request.GET.get('product_type', '0')
    application_type = request.GET.getlist('application_type', ['0'])
    manufacturer = request.GET.get('manufacturer', '0')
    sort = request.GET.get('sort', 'none')


  

    # filter products
    pTyped_products = parse_pt(product_type)
    aTyped_products = parse_at(application_type, pTyped_products)
    for_sale_products = parse_for_sale(for_sale, aTyped_products)
    filtered_products = parse_manufacturer(manufacturer, for_sale_products)
    sorted_products = sort_products(sort, filtered_products)
    products_serialized = ProductSerializer(sorted_products, many=True)
 

    # filter application types
    application_types = Application.objects.all()
    refined_ats = type_refiner(
                                ApplicationAreaSerializer, 
                                application_types, 
                                filtered_products, 
                                'application'
                                )

    # filter manufacturers
    manufacturers = Manufacturer.objects.all()
    refined_manu = type_refiner(
                                ManufacturerSerializer, 
                                manufacturers, 
                                for_sale_products, 
                                'manufacturer'
                                )

    # filter product types
    product_types = ProductType.objects.all()
    refined_pts = type_refiner(
                                ProductTypeSerializer, 
                                product_types, 
                                filtered_products, 
                                'product'
                                )

    filter_content = {
        "for_sale" : for_sale,
        "product_count" : filtered_products.count()
    } 

    return Response({
                    "filter" : [filter_content],
                    "application_types": refined_ats,
                    "product_types": refined_pts,
                    "manufacturers": refined_manu,
                    "products": products_serialized.data
                    })
    
def sort_products(sort, products):
    if sort == 'none':
        return products
    else:
        try:
           sorted_products = products.order_by('sort')
           return sorted_products
        except:
            return products



def parse_pt(product_type):
    products = Product.objects.all()
    if product_type == '0':
        return products
    else:
        return products.filter(product_type=product_type)

def parse_at(application_type, products):
    if application_type == ['0']:
        return products
    else:
        for at in application_type:
            products = products.filter(application=at)
        return products

def parse_manufacturer(manufacturer, products):
    if manufacturer == '0':
        return products
    else:
        return products.filter(manufacturer=manufacturer)


def parse_for_sale(for_sale, products):
    if for_sale == 'true':   
        return products.filter(for_sale=True)
    else:
        return products


def type_refiner(serializer, objects, products, argument):
    serialized_types = []
    for item in objects:
        count = get_argument(item, products, argument)
        at_serialized = serializer(item).data
        at_serialized['count'] = count
        if count > 0:
            at_serialized['enabled'] = True
        serialized_types.append(at_serialized)
    return serialized_types

def get_argument(item, products, argument):
    if argument == 'application':
        return products.filter(application=item).count()
    elif argument == 'product':
        return products.filter(product_type=item).count()
    elif argument == 'manufacturer':
        return products.filter(manufacturer=item).count()

def product_sort(products, argument):
    pass



@api_view(['GET'])
def get_product(request, pk):
    product = Product.objects.get(id=pk)
    serialized_product = ProductSerializer(product)
    return Response({'product': serialized_product.data})


