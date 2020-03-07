''' Products.views.py '''
from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from config.custom_permissions import IsAdminorReadOnly
from ProductFilter.sorter import FilterResponse
from SpecializedProducts.models import ProductSubClass
from .models import Product, ValueCleaner
# from .tasks import add_detail_record
from .serializers import serialize_detail, serialize_detail_quick
from Analytics.models import ProductDetailRecord
# import time
# from django.http import QueryDict
# from config.globals import check_department_string
# from config.tasks import add_supplier_record

@api_view(['POST'])
@permission_classes((IsAdminUser,))
def create_value_cleaner(request: Request, model_type):
    data = request.data
    field = data.get('field')
    new_value = data.get('new_value')
    old_value = data.get('old_value')
    if not (field and new_value and old_value):
        return Response('need field, new value and old value', status=status.HTTP_400_BAD_REQUEST)
    ValueCleaner.objects.create_and_apply_async(
        product_class=model_type,
        field=field,
        new_value=new_value,
        old_value=old_value
        )
    return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
def products_list(request: HttpRequest, product_type: str = None, sub_product: str = None):
    res = FilterResponse.get_cache(request, product_type, sub_product)
    return Response(res, status=status.HTTP_200_OK)
    # location_pk = None
    # if 'supplier_pk' in request.GET:
    #     location_pk = request.GET.get('supplier_pk')
    # if sub_product:
    #     product_type = check_department_string(sub_product)
    # elif product_type:
    #     product_type = check_department_string(product_type)
    # else:
    #     product_type = Product
    # if not product_type:
    #     return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
    # if location_pk:
    #     add_supplier_record.delay(request.get_full_path(), pk=location_pk)
    # query_dict: QueryDict = QueryDict(request.GET.urlencode(), mutable=True)
    # page = 1
    # page_size = 20
    # page_start = (page - 1) * page_size
    # page_end = page * page_size
    # search = None
    # if 'page' in query_dict:
    #     page = query_dict.pop('page')
    # if 'search' in query_dict:
    #     search_string = query_dict.pop('search')
    # path_key = request.path + query_dict.urlencode()
    # res = FilterResponse.get_cache(path_key, page_start, page_end)
    # if res:
    #     print('got res')
    #     return Response(res, status=status.HTTP_200_OK)
    # content = Sorter(product_type, request=request, supplier_pk=location_pk).content
    # content.set_cache(path_key)



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
        pdr = ProductDetailRecord()
        pdr.parse_request(request, product=pk)
        # add_detail_record.delay(request.get_full_path(), pk)
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
    pdr = ProductDetailRecord()
    pdr.parse_request(request, product=pk)
    # add_detail_record.delay(request.get_full_path(), pk)
    return Response(response, status=status.HTTP_200_OK)
