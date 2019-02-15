from rest_framework import serializers
from Addresses.serializers import AddressSerializer
# from Addresses.models import Address
from .models import CustomerProfile, CustomerProduct, CustomerProject
from Products.serializers import ProductDetailSerializer


class CustomerProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(read_only=True, many=True)

    class Meta:
        model = CustomerProfile
        fields = (
            'phone_number',
            'addresses',
            'plan'
            )


class CustomerLibrarySerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = (
            'name',
            'plan',
            'projects',
        )

    def get_projects(self, instance):
        projects = CustomerProject.objects.select_related('address').filter(owner=instance)
        return CustomerProjectSerializer(projects, many=True).data


class CustomerProjectSerializer(serializers.ModelSerializer):
    # products = CustomerProductSerializer(many=True)
    # address = serializers.SerializerMethodField()
    address = AddressSerializer()

    class Meta:
        model = CustomerProject
        fields = (
            'address',
            'nickname',
            'id',
            )


class CustomerProductSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()

    class Meta:
        model = CustomerProduct
        fields = (
            'id',
            'product',
            'use',
            )


class CustomerProjectDetailSerializer(serializers.ModelSerializer):
    products = CustomerProductSerializer(many=True)

    class Meta:
        model = CustomerProject
        fields = (
            'owner',
            'address',
            'nickname',
            'id',
            'products'
            )
