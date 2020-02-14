from enum import Enum
from urllib.parse import unquote
from django.apps import apps
from SpecializedProducts.models import FinishSurface

class BusinessType(Enum):
    RETAILER_LOCATION = 'retailer-location'
    RETAILER_COMPANY ='retailer-company'
    PRO_COMPANY = 'pro-company'

PRODUCT_SUBCLASSES = {
    'FinishSurface': FinishSurface
}

def valid_subclasses():
    return list(PRODUCT_SUBCLASSES.values())

def get_departments():
    return apps.get_app_config('SpecializedProducts').get_models()


def check_department_string(department_string: str):
    department_string = unquote(department_string).lower().strip()
    print(department_string.lower())
    departments = get_departments()
    for dep in departments:
        name = dep._meta.verbose_name_plural.lower().strip()
        print(name)
        if name == department_string:
            print(dep)
            return dep
    return None

    # department = [dep for dep in departments if dep._meta.verbose_name_plural.lower().strip() == department_string.lower()]
    # print(department)
    # if department:
    #     return department[0]
    # return None
