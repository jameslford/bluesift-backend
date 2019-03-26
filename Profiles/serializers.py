import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from Addresses.serializers import AddressSerializer, AddressUpdateSerializer
from Addresses.models import Address, Zipcode
from django.contrib.postgres.search import SearchVector
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
    headquarters = AddressSerializer()
    locations = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()

    class Meta:
        model = CompanyAccount
        fields = (
            'id',
            'headquarters',
            'phone_number',
            'name',
            'shipping_location_count',
            'plan',
            'employees',
            'locations'
        )

    def get_locations(self, instance):
        response_list = []
        employee = self.context.get('employee')
        locations = CompanyShippingLocation.objects.select_related(
            'local_admin',
            'company_account',
            'address',
            'address__postal_code',
            'address__coordinates'
             ).filter(company_account=instance)
        if not locations:
            locations = CompanyShippingLocation.objects.create(company_account=instance)
        for location in locations:
            response_list.append(ShippingLocationListSerializer(location, context={'employee': employee}).data)
        return response_list

    def get_employees(self, instance):
        employees = instance.employees.all()
        return EmployeeProfileSerializer(employees, many=True).data
        # return ShippingLocationListSerializer(locations, many=True, context={'user': user}).data


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
            'pk',
            'company_account',
            'company_name',
            'approved_online_seller',
            'approved_in_store_seller',
            'nickname',
            'product_count',
            'address',
            'phone_number',
            'priced_products',
            'image'
            )

    def get_priced_products(self, instance):
        order = self.context.get('order_by', 'id')
        search_terms = self.context.get('search', None)
        prods = SupplierProduct.objects.filter(supplier=instance).prefetch_related(
            'product',
            'product__swatch_image',
            'product__manufacturer',
            'product__material'
            )
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
            'pk',
            'priced_products',
            'image'
            )

    def get_priced_products(self, instance):
        order = self.context.get('order_by', 'id')
        search_terms = self.context.get('search', None)
        prods = SupplierProduct.objects.filter(supplier=instance).prefetch_related(
            'product',
            'product__swatch_image',
            'product__manufacturer',
            'product__material'
            )
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
                ).filter(search=term).order_by(order)
        else:
            prods = prods.order_by(order)
        return SupplierProductSerializer(prods, many=True).data


class ShippingLocationListSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    editable = serializers.SerializerMethodField()
    deletable = serializers.SerializerMethodField()

    class Meta:
        model = CompanyShippingLocation
        fields = (
            'id',
            'company_account',
            'company_name',
            'address',
            'phone_number',
            'editable',
            'deletable',
            'location_manager',
            'nickname',
            'address_string',
            'product_count',
            'image'
            )

    def get_editable(self, instance):
        employee = self.context.get('employee', None)
        if not employee:
            return False
        if (employee.company_account_owner or
            employee.company_account_admin or
                employee == instance.local_admin):
            return True
        else:
            return False

    def get_deletable(self, instance):
        employee = self.context.get('employee', None)
        if not employee:
            return False
        if (employee.company_account_owner or
                employee.company_account_admin):
            return True
        else:
            return False


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
        address = validated_data.pop('address', None)
        zipcode = address.pop('postal_code', None)
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
        data_add = validated_data.get('address', None)
        if data_add:
            instance.address.address_line_1 = data_add.get('address_line_1', instance.address.address_line_1)
            instance.address.city = data_add.get('city', instance.address.city)
            instance.address.state = data_add.get('state', instance.address.state)
            zipcode = data_add.get('postal_code')
            zipcode = Zipcode.objects.filter(code=zipcode).first()
            if zipcode:
                instance.address.postal_code = zipcode
            instance.address.save()
        instance.nickname = validated_data.get('nickname', instance.nickname)
        image_file = validated_data.get('image', None)
        if image_file:
            file_type = image_file['filetype'].split('/')[0]
            if file_type == 'image':
                imf = ContentFile(base64.b64decode(image_file['file']))
                instance.image.save(image_file['filename'],  imf)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()


class SupplierProductSerializer(serializers.ModelSerializer):
    product = ProductSerializerforSupplier(read_only=True)

    class Meta:
        model = SupplierProduct
        fields = (
            'id',
            'in_store_ppu',
            'units_available_in_store',
            'units_per_order',
            'for_sale_in_store',
            'on_sale',
            'sale_price',
            'banner_item',
            'product'
        )


class SupplierProductUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupplierProduct
        fields = (
            'id',
            'in_store_ppu',
            'units_available_in_store',
            'units_per_order',
            'for_sale_in_store',
            'sale_price',
            'on_sale',
            'banner_item',
        )

    def update(self, instance, validated_data):
        instance.in_store_ppu = validated_data.get('in_store_ppu', instance.in_store_ppu)
        instance.units_available_in_store = validated_data.get('units_available_in_store', instance.units_available_in_store)
        instance.units_per_order = validated_data.get('units_per_order', instance.units_per_order)
        instance.for_sale_in_store = validated_data.get('for_sale_in_store', instance.for_sale_in_store)
        instance.for_sale_online = validated_data.get('for_sale_online', instance.for_sale_online)
        instance.save()
        return instance


class SupplierProductMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupplierProduct
        fields = (
            'id',
            'in_store_ppu',
            'units_available_in_store',
            'units_per_order',
            'location_address',
            'location_id',
            'company_name',
            'lead_time_ts'
        )
