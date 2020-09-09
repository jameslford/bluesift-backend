from Addresses.serializers import AddressSerializer
from Plans.serializers import PlanSerializer
from .models import SupplierCompany


def supplier_company_serializer(company: SupplierCompany):
    return {
        "name": company.name,
        "phone_number": company.phone_number,
        "address": AddressSerializer(company.business_address).data,
        "email_verified": company.email_verified,
        "info": company.info,
        "slug": company.slug,
        "date_created": company.date_created,
        "image": company.image.url if company.image else None,
        "plan": PlanSerializer(company.plan).data,
    }
