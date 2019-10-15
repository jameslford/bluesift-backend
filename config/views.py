from urllib.parse import unquote
from django.apps import apps
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ProductFilter.models import ProductFilter
from Groups.models import ServiceType


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
    return Response({
        'pros': sorted(pro_types, key=lambda k: k['label']),
        'departments': sorted(deps, key=lambda k: k['label'])
        })


@api_view(['GET'])
def get_header_list(request):
    pro_types = list(ServiceType.objects.values_list('label', flat=True))
    departments = [model._meta.verbose_name_plural.title() for model in get_departments()]
    return Response({
        'pros': sorted(pro_types),
        'departments': sorted(departments)
        })
