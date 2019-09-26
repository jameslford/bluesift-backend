"""
serializers used for return project and retailer locations list to user library
"""

from rest_framework import serializers
from Addresses.serializers import AddressSerializer
from Profiles.serializers import RetailerEmployeeShortSerializer
from .models import RetailerLocation


class RetailerLocationListSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    local_admin = RetailerEmployeeShortSerializer()

    class Meta:
        model = RetailerLocation
        fields = [
            'pk',
            'address',
            'address_string',
            'company_name',
            'local_admin'
            'nickname',
            'phone_number',
            'product_count',
            ]


class ProjectListSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    nickname = serializers.CharField()
    deadline = serializers.DateTimeField()
    address = AddressSerializer()
    product_count = serializers.IntegerField()
