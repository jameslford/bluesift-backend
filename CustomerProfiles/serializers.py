from rest_framework import serializers
from Addresses.serializers import AddressSerializer
from Addresses.models import Address
from .models import CustomerProfile, CustomerProduct, CustomerProject
from Products.serializers import ProductDetailSerializer


class CustomerProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(read_only=True, many=True)

    class Meta:
        model = CustomerProfile
        fields = ('phone_number', 'addresses')


class CustomerProductSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()

    class Meta:
        model = CustomerProduct
        fields = (
            'id',
            'product',
            'use',
            )


class CustomerProjectSerializer(serializers.ModelSerializer):
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
