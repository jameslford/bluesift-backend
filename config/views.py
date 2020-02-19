from celery.result import AsyncResult
from django.http.request import HttpRequest
from django.db.models import Count, F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from config.globals import check_department_string
from Profiles.models import LibraryProduct
from Suppliers.models import SupplierProduct, SupplierLocation
from .models import UserTypeStatic, ConfigTree
from .serializers import ProfileSerializer, ShortLib, ProductStatus


@api_view(['GET'])
def pl_status_for_product(request, pk):
    blah = ProductStatus(request.user, pk)
    return Response(blah.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_short_lib(request, pk=None):
    short_lib = ShortLib(request.user, pk)
    return Response(short_lib.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_config(request: HttpRequest):
    user = request.user if request.user and request.user.is_authenticated else None
    conf_tree: ConfigTree = ConfigTree.load()
    res_dict = {
        'profile': ProfileSerializer(user).full_data,
        'departments': conf_tree.product_tree,
        'suppliers': conf_tree.supplier_tree
        }
    return Response(res_dict)


@api_view(['GET'])
def generic_business_list(request: HttpRequest, category=None):
    suppliers = SupplierLocation.objects.select_related(
        'address',
        'address__postal_code',
        'address__coordinates',
        ).prefetch_related(
            'products',
            ).all()
    if category:
        prod_class = check_department_string(category)
        if prod_class is None:
            return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
        supplier_product_pks = prod_class.objects.values('priced__location__pk').distinct()
        suppliers = suppliers.filter(pk__in=supplier_product_pks)
    res = suppliers.annotate(
        product_count=Count('products'),
        lat=F('address__coordinates__lat'),
        lng=F('address__coordinates__lng'),
        address_string=F('address__address_string')
        ).values(
            'nickname',
            'pk',
            'product_count',
            'phone_number',
            'email',
            'lat',
            'lng',
            'address_string'
            )

    return Response(res, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def generic_add(request, collection_pk=None):
    product_pk = request.POST.get('product_pk', None)
    if not product_pk:
        return Response('invalid pk', status=status.HTTP_400_BAD_REQUEST)
    if request.user.is_supplier:
        SupplierProduct.objects.add_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_201_CREATED)
    LibraryProduct.objects.add_product(request.user, product_pk)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def generic_delete(request, product_pk, collection_pk=None):
    if request.user.is_supplier:
        SupplierProduct.objects.delete_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_200_OK)
    LibraryProduct.objects.delete_product(request.user, product_pk)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def landing(request):
    uts = UserTypeStatic.objects.all()
    return Response([ut.serialize() for ut in uts])


@api_view(['GET'])
def task_progress(request):
    job_id = request.GET.get('job_id')
    if not job_id:
        return Response('no job id')
    task = AsyncResult(job_id)
    data = task.state or task.result
    return Response(data)



# @api_view(['GET'])
# def generic_business_detail(request: HttpRequest, category: str, pk: int):

#     if category.lower() == BusinessType.RETAILER_LOCATION.value:
#         model: SupplierLocation = SupplierLocation.objects.select_related(
#             'address',
#             'address__postal_code',
#             'address__coordinates',
#             'company'
#             ).prefetch_related('products', 'products__product').get(pk=pk)
#         add_supplier_record.delay(request.get_full_path(), pk=pk)
#     elif category.lower() == 'retailer-company':
#         model = SupplierCompany.objects.prefetch_related(
#             'employees',
#             'employees__user'
#             ).get(pk=pk)
#     else:
#         return Response('invalid category', status=status.HTTP_400_BAD_REQUEST)
#     return Response(BusinessSerializer(model).getData(), status=status.HTTP_200_OK)