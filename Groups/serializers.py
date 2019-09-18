from typing import Dict
from rest_framework import serializers
from Addresses.serializers import AddressSerializer, AddressUpdateSerializer
from UserProductCollections.models import RetailerLocation
from .models import RetailerCompany, ProCompany
from Profiles.serializers import RetailerEmployeeShortSerializer, ProEmployeeProfileSerializer
# import serpy
# from Addresses.models import Address, Zipcode
# from Groups.models import CompanyAccount

DEFAULT_BUSINESS_LIST_FIELDS = [
    'pk',
    # 'address',
    'coordinates',
    'address_string',
    'phone_number',
    'company_name',
    'nickname',
    ]

RETAILER_LIST = DEFAULT_BUSINESS_LIST_FIELDS + ['product_count']
RETAILER_HEADER = DEFAULT_BUSINESS_LIST_FIELDS + ['product_count', 'product_types']
PRO_LIST = DEFAULT_BUSINESS_LIST_FIELDS + ['service_type']

def serialize_retail_locations(retail_location: RetailerLocation) -> Dict[str, any]:
    return {
        'pk': retail_location.pk,
        'address_string': retail_location.address_string(),
        'coordinates': retail_location.coordinates(),
        'product_count': retail_location.product_count(),
        'phone_number': retail_location.phone_number,
        'company_name': retail_location.company_name()
    }


class RetailerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = RetailerLocation
        fields = tuple(RETAILER_LIST)


class RetailerLocationHeaderSerializer(RetailerListSerializer):

    class Meta:
        model = RetailerLocation
        fields = tuple(RETAILER_HEADER)


class RetailerCompanyHeaderSerializer(serializers.ModelSerializer):
    business_address = AddressSerializer()
    employees = serializers.SerializerMethodField()

    class Meta:
        model = RetailerCompany
        fields = (
            'pk',
            'name',
            'employees',
            'business_address'
        )

    def get_employees(self, instance):
        # employees = instance.prefetch_related('employees').employees.all()
        employees = instance.get_employees()
        return RetailerEmployeeShortSerializer(employees, many=True).data


class ProListSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    address_string = serializers.SerializerMethodField()

    class Meta:
        model = ProCompany
        fields = (
            'pk',
            'coordinates',
            'service_type',
            'phone_number',
            'address_string',
            'company_name',
        )

    def get_address_string(self, instance: ProCompany):
        return instance.business_address.address_string

    def get_company_name(self, instance: ProCompany):
        return instance.name


class ProCompanyDetailSerializers(serializers.ModelSerializer):
    business_address = AddressSerializer()
    employees = serializers.SerializerMethodField()

    class Meta:
        model = ProCompany
        fields = (
            'pk',
            'plan',
            'employees',
            'business_address',
            'phone_number',
            'name',
            )

    def get_employees(self, instance):
        employees = instance.get_employees()
        return ProEmployeeProfileSerializer(employees, many=True).data


# class RetailerListSerializer(serpy.Serializer):
#     pk = serpy.Field()
#     address = AddressSerializer()
#     phone_number = serpy.Field()
#     company_name = serpy.Field()
#     nickname = serpy.Field()
#     prod_count = serpy.Field()


# class RetailerCompanySerializer(serializers.ModelSerializer):
#     address = AddressSerializer(read_only=True)

#     class Meta:
#         model = RetailerCompany
#         fields = ('name', 'phone_number', 'address')


# class CompanyAccountDetailSerializer(serializers.ModelSerializer):
#     headquarters = AddressSerializer()
#     locations = serializers.SerializerMethodField()
#     employees = serializers.SerializerMethodField()

#     class Meta:
#         model = CompanyAccount
#         fields = (
#             'pk',
#             'headquarters',
#             'phone_number',
#             'name',
#             'shipping_location_count',
#             'plan',
#             'employees',
#             'locations'
#         )

#     def get_locations(self, instance):
#         response_list = []
#         employee = self.context.get('employee')
#         locations = CompanyShippingLocation.objects.select_related(
#             'local_admin',
#             'company_account',
#             'address',
#             'address__postal_code',
#             'address__coordinates'
#              ).filter(company_account=instance)
#         if not locations:
#             locations = CompanyShippingLocation.objects.create(company_account=instance)
#         for location in locations:
#             response_list.append(ShippingLocationListSerializer(location, context={'employee': employee}).data)
#         return response_list

#     def get_employees(self, instance):
#         employees = instance.employees.all()
#         return EmployeeProfileSerializer(employees, many=True).data
        # return ShippingLocationListSerializer(locations, many=True, context={'user': user}).data