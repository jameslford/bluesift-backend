from celery.result import AsyncResult
from django.http.request import HttpRequest
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from config.globals import check_department_string
from ProductFilter.models import ProductFilter
from Groups.models import ServiceType, ProCompany, RetailerCompany
from Projects.models import LibraryProduct
from Retailers.models import RetailerProduct, RetailerLocation
from .models import UserTypeStatic
from .tasks import add_retailer_record, add_pro_record
from .serializers import BusinessSerializer, ProfileSerializer, ShortLib, ProductStatus
from .globals import BusinessType


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
    user = request.user if request.user.is_authenticated else None
    pro_types = [serv.custom_serialize() for serv in ServiceType.objects.all()]
    deps = [dep.serialize_pt_attributes() for dep in ProductFilter.objects.all()]
    res_dict = {
        'profile': ProfileSerializer(user).full_data,
        'pros': sorted(pro_types, key=lambda k: k['label']),
        'departments': sorted(deps, key=lambda k: k['label']),
        }
    return Response(res_dict)


@api_view(['GET'])
def generic_business_detail(request: HttpRequest, category: str, pk: int):
    if category.lower() == BusinessType.PRO_COMPANY.value:
        model: ProCompany = ProCompany.objects.select_related(
            'business_address',
            'business_address__postal_code',
            'business_address__coordinates',
            'plan'
            ).get(pk=pk)
        add_pro_record.delay(request.get_full_path(), pk=pk)
    elif category.lower() == BusinessType.RETAILER_LOCATION.value:
        model: RetailerLocation = RetailerLocation.objects.select_related(
            'address',
            'address__postal_code',
            'address__coordinates',
            'company'
            ).prefetch_related('products', 'products__product').get(pk=pk)
        add_retailer_record.delay(request.get_full_path(), pk=pk)
    elif category.lower() == 'retailer-company':
        model = RetailerCompany.objects.prefetch_related(
            'employees',
            'employees__user'
            ).get(pk=pk)
    return Response(BusinessSerializer(model).getData(), status=status.HTTP_200_OK)


@api_view(['GET'])
def generic_business_list(request: HttpRequest, category: str):
    service_type = request.GET.get('service_type', None)

    if 'retailer' in category.lower():
        retailers = RetailerLocation.objects.select_related(
            'address',
            'address__postal_code',
            'address__coordinates',
            ).prefetch_related(
                'products',
                ).all().annotate(prod_count=Count('products'))
        if service_type:
            prod_class = check_department_string(service_type)
            if prod_class is None:
                return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
            retailer_product_pks = prod_class.objects.values('priced__retailer__pk').distinct()
            retailers = retailers.filter(pk__in=retailer_product_pks)
        return Response(
            [BusinessSerializer(ret, False).getData() for ret in retailers],
            status=status.HTTP_200_OK)

    if 'pro' in category.lower():
        services = ProCompany.objects.select_related(
            'service',
            'business_address',
            'business_address__postal_code',
            'business_address__coordinates'
        ).all()
        if service_type:
            services = services.filter(service__label__iexact=service_type)
        return Response(
            [BusinessSerializer(serv).getData() for serv in services],
            status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def generic_add(request, collection_pk=None):
    product_pk = request.POST.get('product_pk', None)
    if not product_pk:
        return Response('invalid pk', status=status.HTTP_400_BAD_REQUEST)
    if request.user.is_supplier:
        RetailerProduct.objects.add_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_201_CREATED)
    LibraryProduct.objects.add_product(request.user, product_pk)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def generic_delete(request, product_pk, collection_pk=None):
    if request.user.is_supplier:
        RetailerProduct.objects.delete_product(request.user, product_pk, collection_pk)
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


    # user = request.user
    # blank_slib = ShortLib(0, [], [])
    # if not user.is_authenticated:
    #     return Response(asdict(blank_slib), status=status.HTTP_200_OK)
    # collections = user.get_collections()
    # collection = collections.get(pk=pk) if pk else collections.first()
    # if not collection:
    #     return Response(asdict(blank_slib), status=status.HTTP_200_OK)
    # selected_proj_loc = PLShort(collection.nickname, collection.pk)
    # pl_list = collections.values('nickname', 'pk')
    # product_ids = collection.products.values_list('product__pk', flat=True)
    # short_lib = ShortLib(
    #     count=collections.count(),
    #     product_ids=product_ids,
    #     pl_short_list=pl_list,
    #     selected_location=selected_proj_loc
    #     )