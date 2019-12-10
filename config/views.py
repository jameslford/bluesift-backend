from urllib.parse import unquote
from celery.result import AsyncResult
from django.apps import apps
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ProductFilter.models import ProductFilter
from Groups.models import ServiceType
from .models import LibraryLink, UserTypeStatic


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
def get_expanded_header(request):
    pro_types = [serv.serialize() for serv in ServiceType.objects.all()]
    deps = [dep.serialize_pt_attributes() for dep in ProductFilter.objects.all()]
    response_dict = {
        'pros': sorted(pro_types, key=lambda k: k['label']),
        'departments': sorted(deps, key=lambda k: k['label']),
        }
    if request.user.is_authenticated:
        if request.user.is_supplier:
            response_dict['business'] = request.user.get_group().serialize()
            term = {'for_supplier': True}
        elif request.user.is_pro:
            response_dict['business'] = request.user.get_group().serialize()
            term = {'for_pro': True}
        elif request.user.admin:
            term = {'for_admin': True}
        else:
            term = {'for_user': True}
        response_dict['libraryLinks'] = [link.serialize() for link in LibraryLink.objects.filter(**term)]
    return Response(response_dict)


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
    print(data)
    return Response(data)
