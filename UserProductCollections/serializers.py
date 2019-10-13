"""
serializers used for return project and retailer locations list to user library
"""

from rest_framework import serializers
from Addresses.serializers import AddressSerializer


class ProjectListSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    nickname = serializers.CharField()
    deadline = serializers.DateTimeField()
    address = AddressSerializer()
    product_count = serializers.IntegerField()
