from rest_framework import serializers
from Addresses.serializers import AddressSerializer
from Addresses.models import Address
from Products.serializers import ProductSerializerforSupplier
from .models import (
    CompanyAccount,
    CompanyShippingLocation,
    EmployeeProfile,
    SupplierProduct,
    )


class CompanyAccountSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)

    class Meta:
        model = CompanyAccount
        fields = ('name', 'phone_number', 'address')


class CompanyAccountDetailSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    locations = serializers.SerializerMethodField()
    count = None

    class Meta:
        model = CompanyAccount
        fields = (
            'address',
            'phone_number',
            'name',
            'count'
            'plan',
            'locations'
        )

    def get_locations(self, instance):
        locations = instance.shipping_locations.all()
        if not locations:
            locations = CompanyShippingLocation.objects.create(company_account=instance)
        self.count = locations.count()
        return ShippingLocationListSerializer(locations, many=True).data


class EmployeeProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeProfile
        fields = (
            'id',
            'title',
            'name',
            'email',
            'company_account_owner',
            'company_account_admin',
        )




class SVLocationSerializer(serializers.ModelSerializer):
    priced_products = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)

    class Meta:
        model = CompanyShippingLocation
        fields = (
            'company_account',
            'company_name',
            'approved_online_seller',
            'approved_in_store_seller',
            'nickname',
            'product_count',
            'address',
            'phone_number',
            'id',
            'priced_products',
            'image'
            )

    def get_priced_products(self, instance, order='id'):
        prods = instance.priced_products.all().order_by(order)
        return SupplierProductSerializer(prods, many=True).data


class ShippingLocationListSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    local_admin = EmployeeProfileSerializer()

    class Meta:
        model = CompanyShippingLocation
        fields = (
            'id',
            'company_account',
            'company_name',
            'address',
            'phone_number',
            'local_admin',
            'nickname',
            'address_string',
            'product_count',
            'image'
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

    def create(self, account, validated_data):
        address = validated_data.pop('address')
        address = Address.objects.create(**address)
        return CompanyShippingLocation.objects.create(
            address=address,
            company_account=account,
            **validated_data
            )


class SupplierProductSerializer(serializers.ModelSerializer):
    product = ProductSerializerforSupplier(read_only=True)

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
