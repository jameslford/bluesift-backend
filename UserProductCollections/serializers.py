import base64
import serpy
from rest_framework import serializers
from django.contrib.postgres.search import SearchVector
from django.core.files.base import ContentFile
from Addresses.models import Address, Zipcode
from Addresses.serializers import AddressSerializer, AddressUpdateSerializer
from Profiles.serializers import RetailerEmployeeShortSerializer
from .models import RetailerLocation


COMMON_RETAILER_LOCATION_FIELDS = [
    'pk',
    'company_name',
    'address',
    'phone_number',
    'nickname',
    'address_string',
    'product_count',
    ]


class RetailerLocationDetailSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = RetailerLocation
        fields = tuple(COMMON_RETAILER_LOCATION_FIELDS + [
            'local_admin',
            'product_types'
            ])


class RetailerLocationListSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    local_admin = RetailerEmployeeShortSerializer()

    class Meta:
        model = RetailerLocation
        fields = tuple(COMMON_RETAILER_LOCATION_FIELDS + [
            'local_admin',
            ])


class ProjectSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    nickname = serializers.CharField()
    deadline = serializers.DateTimeField()
    address = AddressSerializer()
    product_count = serializers.IntegerField()


# class ProjectDetailSerilizer(serializers.ModelSerializer):
#     pass


# class SVLocationSerializer(serializers.ModelSerializer):
#     priced_products = serializers.SerializerMethodField()
#     address = AddressSerializer(read_only=True)

#     class Meta:
#         model = CompanyShippingLocation
#         fields = (
#             'pk',
#             'company_account',
#             'company_name',
#             'approved_in_store_seller',
#             'nickname',
#             'product_count',
#             'average_rating',
#             'rating_count',
#             'address',
#             'phone_number',
#             'priced_products',
#             )

#     def get_priced_products(self, instance):
#         order = self.context.get('order_by', 'pk')
#         search_terms = self.context.get('search', None)
#         prods = SupplierProduct.objects.filter(supplier=instance).prefetch_related(
#             'product',
#             'product__manufacturer',
#             )
#         if search_terms:
#             for term in search_terms:
#                 prods = prods.annotate(
#                     search=SearchVector(
#                         'product__name',
#                         'product__manufacturer__label',
#                         'product__manufacturer_style',
#                         'product__manufacturer_sku',
#                         'product__manu_collection',
#                         'product__material__label'
#                     )
#                 ).filter(search=term)
#         else:
#             prods = prods.order_by(order)
#         return SupplierProductSerializer(prods, many=True).data


# class CVLocationSerializer(serializers.ModelSerializer):
#     priced_products = serializers.SerializerMethodField()
#     address = AddressSerializer(read_only=True)

#     class Meta:
#         model = CompanyShippingLocation
#         fields = (
#             'company_account',
#             'company_name',
#             'approved_online_seller',
#             'approved_in_store_seller',
#             'nickname',
#             'product_count',
#             'address',
#             'phone_number',
#             'pk',
#             'priced_products',
#             'image'
#             )

#     def get_priced_products(self, instance):
#         order = self.context.get('order_by', 'pk')
#         search_terms = self.context.get('search', None)
#         prods = SupplierProduct.objects.filter(supplier=instance).prefetch_related(
#             'product',
#             'product__swatch_image',
#             'product__manufacturer',
#             # 'product__material'
#             )
#         if search_terms:
#             for term in search_terms:
#                 prods = prods.annotate(
#                     search=SearchVector(
#                         'product__name',
#                         'product__manufacturer__label',
#                         'product__manufacturer_color',
#                         'product__manu_collection',
#                         'product__material__label'
#                     )
#                 ).filter(search=term).order_by(order)
#         else:
#             prods = prods.order_by(order)
#         return SupplierProductSerializer(prods, many=True).data


# class ShippingLocationListSerializer(serializers.ModelSerializer):
#     address = AddressSerializer()
#     editable = serializers.SerializerMethodField()
#     deletable = serializers.SerializerMethodField()

#     class Meta:
#         model = CompanyShippingLocation
#         fields = (
#             'pk',
#             'company_account',
#             'company_name',
#             'address',
#             'phone_number',
#             'editable',
#             'deletable',
#             'location_manager',
#             'nickname',
#             'address_string',
#             'product_count',
#             'image'
#             )

#     def get_editable(self, instance):
#         employee = self.context.get('employee', None)
#         if not employee:
#             return False
#         return bool(
#             employee.company_account_owner or
#             employee.company_account_admin or
#             employee == instance.local_admin)

#     def get_deletable(self, instance):
#         employee = self.context.get('employee', None)
#         if not employee:
#             return False
#         return bool(
#             employee.company_account_owner or
#             employee.company_account_admin)


# class ShippingLocationUpdateSerializer(serializers.ModelSerializer):
#     address = AddressUpdateSerializer()

#     class Meta:
#         model = CompanyShippingLocation
#         fields = (
#             'address',
#             'nickname',
#             'phone_number'
#         )

#     def create(self, account, validated_data):
#         address = validated_data.pop('address', None)
#         zipcode = address.pop('postal_code', None)
#         code = zipcode.get('code', None)
#         zipcode = Zipcode.objects.filter(code=code).first()
#         if not zipcode:
#             return 'Invalid Zip'
#         address = Address.objects.create(postal_code=zipcode, **address)
#         return CompanyShippingLocation.objects.create(
#             address=address,
#             company_account=account,
#             **validated_data
#             )

#     def update(self, instance, validated_data):
#         data_add = validated_data.get('address', None)
#         if data_add:
#             instance.address.address_line_1 = data_add.get('address_line_1', instance.address.address_line_1)
#             instance.address.city = data_add.get('city', instance.address.city)
#             instance.address.state = data_add.get('state', instance.address.state)
#             zipcode = data_add.get('postal_code')
#             zipcode = Zipcode.objects.filter(code=zipcode).first()
#             if zipcode:
#                 instance.address.postal_code = zipcode
#             instance.address.save()
#         instance.nickname = validated_data.get('nickname', instance.nickname)
#         image_file = validated_data.get('image', None)
#         if image_file:
#             file_type = image_file['filetype'].split('/')[0]
#             if file_type == 'image':
#                 imf = ContentFile(base64.b64decode(image_file['file']))
#                 instance.image.save(image_file['filename'], imf)
#         instance.phone_number = validated_data.get('phone_number', instance.phone_number)
#         instance.save()
