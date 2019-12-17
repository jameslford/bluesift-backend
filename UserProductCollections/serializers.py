"""
serializers used for return project and retailer locations list to user library
"""

from rest_framework import serializers
from Addresses.serializers import AddressSerializer


def serialize_project(project):
    return {
        'pk' : project.pk,
        'image' : project.image.url if project.image else None,
        'nickname' : project.nickname,
        'deadline' : project.deadline,
        'address' : AddressSerializer(project.address).data,
        'product_count' : project.product_count(),
    }


class ProjectListSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    nickname = serializers.CharField()
    deadline = serializers.DateTimeField()
    address = AddressSerializer()
    product_count = serializers.IntegerField()
