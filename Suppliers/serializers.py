from Addresses.serializers import AddressSerializer
from .models import SupplierLocation
from Profiles.serializers import employee_mini_serializer

def serialize_location_public_detail(business: SupplierLocation):
    employees = business.company.employees.all()
    return {
        'email': business.email,
        'pk': business.pk,
        'phone_number': business.phone_number,
        'name': business.nickname,
        'image': business.image.url if business.image else None,
        'address': AddressSerializer(business.address).data,
        'employees': [employee_mini_serializer(emp) for emp in employees],
        'info': business.company.info
        }

def serialize_location_private_detail(business: SupplierLocation):
    employees = business.company.employees.all()
    return {
        'email': business.email,
        'pk': business.pk,
        'phone_number': business.phone_number,
        'name': business.nickname,
        'image': business.image.url if business.image else None,
        'address': AddressSerializer(business.address).data,
        'employees': [employee_mini_serializer(emp) for emp in employees],
        'info': business.company.info,
        'views': business.view_records()
        }
