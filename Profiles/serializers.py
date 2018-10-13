from rest_framework import serializers
from Addresses.serializers import AddressSerializer
from .models import(
    CompanyAccount,
    CompanyShippingLocation,
    SupplierProduct,
    CustomerProfile,
    CustomerProject,
    CustomerProduct
    )
from Products.serializers import ProductDetailSerializer


class CompanyAccountSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    class Meta:
        model = CompanyAccount
        fields = ('name', 'phone_number', 'address')

class CustomerProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(read_only=True, many=True)
    class Meta:
        model = CustomerProfile
        fields = ('phone_number', 'addresses')


class CustomerProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = (
            'id',
            'product',
            'use',
            'project',
            'product_name',
            'product_id',
            'product_image',
            'product_category',
            'product_build',
            'product_material',
            'product_lowest_price',
            'product_for_sale'
            )

class CustomerProjectSerializer(serializers.ModelSerializer):
    products = CustomerProductSerializer(many=True)
    class Meta:
        model = CustomerProject
        fields = ('owner', 'address', 'nickname', 'id', 'products')

class SupplierProductSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)
    class Meta:
        model = SupplierProduct
        fields = (
            'id',
            'my_price',
            'price_per_unit',
            'units_available',
            'units_per_order',
            'for_sale',
            'product'
            # 'product_name',
            # 'product_id',
            # 'product_image',
            # 'product_category',
            # 'product_build',
            # 'product_material',
            # 'product_lowest_price'
        )

class ShippingLocationSerializer(serializers.ModelSerializer):
    priced_products = SupplierProductSerializer(many=True, read_only=True)
    class Meta:
        model = CompanyShippingLocation
        fields = ('company_account', 'approved_seller', 'nickname', 'address', 'id', 'priced_products')
