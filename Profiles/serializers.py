from rest_framework import serializers
from Addresses.serializers import AddressSerializer, AddressUpdateSerializer
from Addresses.models import Address, Zipcode
from django.contrib.postgres.search import SearchVector
from Products.serializers import ProductSerializerforSupplier, ProductDetailSerializer
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
    headquarters = AddressSerializer()
    locations = serializers.SerializerMethodField()

    class Meta:
        model = CompanyAccount
        fields = (
            'id',
            'headquarters',
            'phone_number',
            'name',
            'shipping_location_count',
            'plan',
            'locations'
        )

    def get_locations(self, instance):
        locations = instance.shipping_locations.all()
        if not locations:
            locations = CompanyShippingLocation.objects.create(company_account=instance)
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

    def get_priced_products(self, instance):
        order = self.context.get('order_by', 'id')
        search_terms = self.context.get('search', None)
        prods = SupplierProduct.objects.filter(supplier=instance).prefetch_related('product', 'product__swatch_image')
        if search_terms:
            for term in search_terms:
                prods = prods.annotate(
                    search=SearchVector(
                        'product__name',
                        'product__manufacturer__label',
                        'product__manufacturer_color',
                        'product__manu_collection',
                        'product__material__label'
                    )
                ).filter(search=term)
        else:
            prods = prods.order_by(order)
        return SupplierProductSerializer(prods, many=True).data


class CVLocationSerializer(serializers.ModelSerializer):
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

    def get_priced_products(self, instance):
        order = self.context.get('order_by', 'id')
        prods = instance.priced_products.filter(for_sale_in_store=True).order_by(order)
        return CVSupplierProductSerializer(prods, many=True).data


class ShippingLocationListSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    # local_admin = EmployeeProfileSerializer()

    class Meta:
        model = CompanyShippingLocation
        fields = (
            'id',
            'company_account',
            'company_name',
            'address',
            'phone_number',
            # 'local_admin',
            'nickname',
            'address_string',
            'product_count',
            'image'
            )


class ShippingLocationUpdateSerializer(serializers.ModelSerializer):
    address = AddressUpdateSerializer()

    class Meta:
        model = CompanyShippingLocation
        fields = (
            'address',
            'nickname',
            'phone_number'
        )

    def create(self, account, validated_data):
        address = validated_data.pop('address')
        zipcode = address.pop('postal_code')
        zipcode = Zipcode.objects.filter(code=zipcode).first()
        if not zipcode:
            return 'Invalid Zip'
        address = Address.objects.create(postal_code=zipcode, **address)
        return CompanyShippingLocation.objects.create(
            address=address,
            company_account=account,
            **validated_data
            )

    def update(self, instance, validated_data):
        instance_address = instance.address
        data_add = validated_data.get('address', None)
        if data_add:
            instance_address.address_line_1 = data_add.get('address_line_1', instance_address.address_line_1)
            instance_address.city = data_add.get('city', instance_address.city)
            instance_address.state = data_add.get('state', instance_address.state)
            instance_address.postal_code = data_add.get('postal_code', instance_address.postal_code)
            instance_address.save()
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()


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


class CVSupplierProductSerializer(serializers.ModelSerializer):
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


class SupplierProductMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupplierProduct
        fields = (
            'id',
            'my_price',
            'online_ppu',
            'units_available',
            'units_per_order',
            'location_address',
            'location_id',
            'company_name',
            'coordinates'
        )
