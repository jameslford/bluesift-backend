from rest_framework import serializers
from Addresses.serializers import AddressSerializer
from Addresses.models import Address
from Products.serializers import ProductDetailSerializer
from .models import(
    CompanyAccount,
    CompanyShippingLocation,
    SupplierProduct,
    CustomerProfile,
    CustomerProject,
    CustomerProduct
    )


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

class SupplierProductSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)
    class Meta:
        model = SupplierProduct
        fields = (
            'id',
            'my_price',
            'online_ppu',
            'units_available',
            'units_per_order',
            'for_sale_online',
            'for_sale_in_store',
            'product'
        )

class ShippingLocationDetailSerializer(serializers.ModelSerializer):
    priced_products = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)
    class Meta:
        model = CompanyShippingLocation
        fields = (
            'company_account',
            'company_name',
            'approved_online_seller',
            'nickname',
            'product_count',
            'address',
            'phone_number',
            'id',
            'priced_products',
            'image'
            )
    def get_priced_products(self, instance):
        prods = instance.priced_products.all().order_by('id')
        return SupplierProductSerializer(prods, many=True).data

class ShippingLocationSerializer(serializers.ModelSerializer):
    address = AddressSerializer()    
    class Meta:
        model = CompanyShippingLocation
        fields = (
            'id',
            'company_account',
            'company_name',
            'address',
            'nickname',
            'address_string',
            )


class ShippingLocationUpdateSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = CompanyShippingLocation
        fields = (
            'company_account',
            'address',
            'nickname',
            'phone_number'
        )

    def create(self, validated_data):
        address = validated_data.pop('address')
        address = Address.objects.create(**address)
        return CompanyShippingLocation.objects.create(address=address, **validated_data)

class SupplierProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProduct
        fields = (
            'id',
            'my_price',
            'units_available',
            'units_per_order',
            'for_sale_in_store',
            'for_sale_online'
        )

    def update(self, instance, validated_data):
        instance.my_price = validated_data.get('my_price', instance.my_price)
        instance.units_available = validated_data.get('units_available', instance.units_available)
        instance.units_per_order = validated_data.get('units_per_order', instance.units_per_order)
        instance.for_sale_in_store = validated_data.get('for_sale_in_store', instance.for_sale_in_store)
        instance.for_sale_online = validated_data.get('for_sale_online', instance.for_sale_online)
        instance.save()
        return instance



