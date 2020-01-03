from urllib.parse import unquote
from celery.result import AsyncResult
from django.apps import apps
from django.http.request import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from Accounts.serializers import user_serializer
from ProductFilter.models import ProductFilter
from Groups.models import ServiceType
from Profiles.serializers import serialize_profile
from Projects.models import ProjectProduct
from Retailers.models import RetailerProduct
from .models import UserTypeStatic


def get_departments():
    return apps.get_app_config('SpecializedProducts').get_models()


def check_department_string(department_string: str):
    department_string = unquote(department_string)
    departments = get_departments()
    department = [dep for dep in departments if dep._meta.verbose_name_plural.lower() == department_string.lower()]
    if department:
        return department[0]
    return None


@api_view(['GET'])
def user_config(request: HttpRequest):
    user = request.user if request.user.is_authenticated else None
    library_links = user.get_library_links() if user else None
    business = user.get_group().custom_serialize() if user and (user.is_pro or user.is_supplier) else None
    pro_types = [serv.custom_serialize() for serv in ServiceType.objects.all()]
    deps = [dep.serialize_pt_attributes() for dep in ProductFilter.objects.all()]
    collections = user.get_collections().values('pk', 'nickname')
    user_res = user_serializer(user) if user else None
    res_dict = {
        'user': user_res,
        'profile': serialize_profile(request.user),
        'pros': sorted(pro_types, key=lambda k: k['label']),
        'departments': sorted(deps, key=lambda k: k['label']),
        'collections': collections,
        'business': business,
        'libraryLinks': library_links
        }
    return Response(res_dict)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def generic_add(request, collection_pk=None):
    product_pk = request.POST.get('product_pk', None)
    if not product_pk:
        return Response('invalid pk', status=status.HTTP_400_BAD_REQUEST)
    if request.user.is_supplier:
        RetailerProduct.objects.add_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_201_CREATED)
    ProjectProduct.objects.add_product(request.user, product_pk, collection_pk)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def generic_delete(request, product_pk, collection_pk=None):
    if request.user.is_supplier:
        RetailerProduct.objects.delete_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_200_OK)
    ProjectProduct.objects.delete_product(request.user, product_pk, collection_pk)
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
