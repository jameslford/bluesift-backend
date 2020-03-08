from Suppliers.serializers import serialize_location_public_detail
from Addresses.serializers import AddressSerializer
from Plans.serializers import PlanSerializer
from Profiles.serializers import employee_mini_serializer
from .models import SupplierCompany


def supplier_company_serializer(company: SupplierCompany):
    return {
        'name': company.name,
        'phone_number': company.phone_number,
        'address': AddressSerializer(company.business_address).data,
        'email_verified': company.email_verified,
        'info': company.info,
        'slug': company.slug,
        'date_created': company.date_created,
        'image': company.image.url if company.image else None,
        'plan': PlanSerializer(company.plan).data,
        'employees': [employee_mini_serializer(emp) for emp in company.employees.all()],
        'locations': [serialize_location_public_detail(loc) for loc in company.shipping_locations.all()]
        }
