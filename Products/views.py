''' Products.views.py '''
from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from config.globals import check_department_string
from config.tasks import add_supplier_record
from config.custom_permissions import IsAdminorReadOnly
from ProductFilter.sorter import Sorter
from SpecializedProducts.models import ProductSubClass
from .models import Product, ValueCleaner
from .tasks import add_detail_record
from .serializers import serialize_detail, serialize_detail_quick

@api_view(['POST'])
@permission_classes((IsAdminUser,))
def create_value_cleaner(request: Request, model_type):
    product_type = check_department_string(model_type)
    data = request.data
    field = data.get('field')
    new_value = data.get('new_value')
    old_value = data.get('old_value')
    if not (field and new_value and old_value):
        return Response('need field, new value and old value', status=status.HTTP_400_BAD_REQUEST)
    ValueCleaner.objects.create_and_apply(product_type, field, old_value, new_value)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
def products_list(request: HttpRequest, product_type: str = None, sub_product: str = None):
    location_pk = None
    if 'location_pk' in request.GET:
        location_pk = request.GET.get('location_pk')
    if sub_product:
        product_type = check_department_string(sub_product)
    elif product_type:
        product_type = check_department_string(product_type)
    else:
        product_type = Product
    if not product_type:
        return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
    if location_pk:
        add_supplier_record.delay(request.get_full_path(), pk=location_pk)
    content = Sorter(product_type, request=request, supplier_pk=location_pk)
    return Response(content.serialized, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes((IsAdminorReadOnly,))
def product_detail(request, pk):

    product: ProductSubClass = Product.subclasses.get_subclass(pk=pk)

    if request.method == 'GET':
        response = serialize_detail(product)
        if request.user.is_authenticated and request.user.is_admin:
            response.update({
                'admin_fields' : product.get_admin_fields()
            })
        add_detail_record.delay(request.get_full_path(), pk)
        return Response(response, status=status.HTTP_200_OK)

    if request.method == 'POST':
        for k, v in request.data.items():
            setattr(product, k, v)
        product.save()
        response = serialize_detail(product)
        admin_fields = product.get_admin_fields()
        response.update({
            'admin_fields' : admin_fields
        })
        return Response(response, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def product_detail_quick(request, pk):
    product = Product.subclasses.get_subclass(pk=pk)
    response = serialize_detail_quick(product)
    add_detail_record.delay(request.get_full_path(), pk)
    return Response(response, status=status.HTTP_200_OK)
