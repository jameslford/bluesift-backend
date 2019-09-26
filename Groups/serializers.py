from typing import Dict
from rest_framework import serializers
from Addresses.serializers import AddressSerializer
from Profiles.serializers import RetailerEmployeeShortSerializer, ProEmployeeProfileSerializer
from UserProductCollections.models import RetailerLocation
from .models import RetailerCompany, ProCompany


DEFAULT_BUSINESS_LIST_FIELDS = [
    'pk',
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
        fields = [
            'pk',
            'address_string',
            'company_name',
            'coordinates',
            'nickname',
            'phone_number',
            'product_count'
            ]


class RetailerLocationHeaderSerializer(RetailerListSerializer):

    class Meta:
        model = RetailerLocation
        fields = [
            'pk',
            'address_string',
            'coordinates',
            'company_name',
            'nickname',
            'phone_number',
            'product_count',
            'product_types'
            ]


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
        employees = instance.get_employees()
        return RetailerEmployeeShortSerializer(employees, many=True).data


class ProListSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    address_string = serializers.SerializerMethodField()

    class Meta:
        model = ProCompany
        fields = (
            'pk',
            'address_string',
            'coordinates',
            'company_name',
            'phone_number',
            'service_type',
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
            'business_address',
            'employees',
            'name',
            'phone_number',
            'plan',
            )

    def get_employees(self, instance):
        employees = instance.get_employees()
        return ProEmployeeProfileSerializer(employees, many=True).data
