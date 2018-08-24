from rest_framework import serializers
from .models import(
    CompanyAccount,
    CompanyShippingLocation,
    SupplierProduct,
    CustomerProfile,
    CustomerProject,
    CustomerProduct
    )


class CompanyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAccount

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile


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
    class Meta:
        model = SupplierProduct
        fields = (
            'my_price'
            'price_per_unit',
            'units_available',
            'units_per_order',
            'for sale',
            'product_name',
            'product_id',
            'product_image',
            'product_category',
            'product_build',
            'product_material',
            'product_lowest_price'
        )

class ShippingLocationSerializer(serializers.ModelSerializer):
    products = SupplierProductSerializer(many=True)
    class Meta:
        model = CompanyShippingLocation
        fields = ('company_account', 'approved_seller', 'nickname', 'address', 'id', 'products')
