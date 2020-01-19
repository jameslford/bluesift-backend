''' Products.views.py '''
from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from config.globals import check_department_string
from config.tasks import add_supplier_record
from config.custom_permissions import IsAdminorReadOnly
from ProductFilter.sorter import Sorter
from .models import Product
from .tasks import add_detail_record
from .serializers import serialize_detail, serialize_detail_quick


@api_view(['GET'])
def products_list(request: HttpRequest, product_type: str, location_pk: int = None, update=False):
    product_type = check_department_string(product_type)
    if not product_type:
        return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
    if location_pk:
        add_supplier_record.delay(request.get_full_path(), pk=location_pk)
    content = Sorter(product_type, request=request, location_pk=location_pk, update=update)
    return Response(content(), status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes((IsAdminorReadOnly,))
def product_detail(request, pk):

    product = Product.subclasses.get_subclass(pk=pk)

    if request.method == 'GET':
        response = serialize_detail(product)
        if request.user.is_authenticated and request.user.is_admin:
            admin_fields = product.get_admin_fields()
            response.update({
                'admin_fields' : admin_fields
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
