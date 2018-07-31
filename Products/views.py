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
                    Application, 
                    Manufacturer, 
                    ProductType
                    )



@api_view(['GET'])
def product_list(request):

    # parse request
    is_priced = request.GET.get('is_priced', 'False')
    product_type = request.GET.get('product_type', '0')
    application_type = request.GET.getlist('application_type', ['0'])
    manufacturer = request.GET.getlist('manufacturer', ['0'])

    # structure filter objects
  

    # filter products
    pTyped_products = parse_pt(product_type)
    aTyped_products = parse_at(application_type, pTyped_products)
    mTyped_products = parse_manufacturer(manufacturer, aTyped_products)
    filtered_products = parse_priced(is_priced, mTyped_products)
    products_serialized = ProductSerializer(filtered_products, many=True)
 

    # filter application types
    application_types = Application.objects.all()
    refined_ats = type_refiner(ApplicationAreaSerializer, application_types, filtered_products, 'application')

    # filter manufacturers
    manufacturers = Manufacturer.objects.all()
    refined_manu = type_refiner(ManufacturerSerializer, manufacturers, aTyped_products, 'manufacturer')

    # filter product types
    product_types = ProductType.objects.all()
    refined_pts = type_refiner(ProductTypeSerializer, product_types, filtered_products, 'product')

    filter_content = {
        "is_priced" : is_priced,
        "product_count" : filtered_products.count()
    } 

    return Response({
                    "filter" : [filter_content],
                    "application_types": refined_ats,
                    "product_types": refined_pts,
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
    if application_type == ['0']:
        return products
    else:
        for at in application_type:
            products = products.filter(application=at)
        return products

def parse_manufacturer(manufacturer, products):
    if manufacturer == ['0']:
        return products
    else:
        query = Q(manufacturer=manufacturer[0])
        for manu in manufacturer[1:]:
            query |= Q(manufacturer=manu)
        return products.filter(query)


def parse_priced(is_priced, products):
    if is_priced == 'true':   
        return products.filter(is_priced=True)
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








@api_view(['GET'])
def get_product(request, pk):
    product = Product.objects.get(id=pk)
    serialized_product = ProductSerializer(product)
    return Response({'product': serialized_product.data})


