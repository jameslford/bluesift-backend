import serpy
from rest_framework import serializers
from UserProducts.models import RetailerProduct


class DurationField(serpy.Field):
    """ for converting django.models.DurationField to  days"""
    def to_value(self, value):
        return str(value.days)

class TitleField(serpy.Field):
    """ turns string values to titlecase """
    def to_value(self, value: str):
        return value.lower().title()

class FullRetailerProductSerializer(serpy.Serializer):
    pk = serpy.Field()
    in_store_ppu = serpy.Field()
    online_ppu = serpy.Field()
    units_available_in_store = serpy.Field()
    units_per_order = serpy.Field()
    lead_time_ts = DurationField()
    offer_installation = serpy.Field()
    publish_in_store_availability = serpy.Field()
    publish_in_store_price = serpy.Field()
    publish_online_price = serpy.Field()

    product_pk = serpy.MethodField()
    unit = serpy.MethodField()
    manufacturer_style = serpy.MethodField()
    manufacturer_collection = serpy.MethodField()
    manufacturer_sku = serpy.MethodField()
    swatch_image = serpy.MethodField()
    manufacturer = serpy.MethodField()


    def get_manufacturer_style(self, obj):
        """ gets manufacturer_style from retailer.product object """
        return obj.product.manufacturer_style.lower().title()

    def get_manufacturer_sku(self, obj):
        """ gets manufacturer_sku from retailer.product object """
        return obj.product.manufacturer_sku

    def get_manufacturer(self, obj):
        """ gets manufacturer.label from retailer.product object """
        return obj.product.manufacturer.label

    def get_manufacturer_collection(self, obj):
        """ gets manu_collection from retailer.product object """
        return obj.product.manu_collection.lower().title()

    def get_unit(self, obj):
        """ gets unit from retailer.product object """
        return obj.product.unit

    def get_product_pk(self, obj):
        """ gets pk from retailer.product object """
        return str(obj.product.pk)

    def get_swatch_image(self, prod_obj):
        """ gets swatch_image.url from retailer.product object """
        if prod_obj.product.swatch_image:
            return prod_obj.product.swatch_image.url
        return None


class RetailerProductMiniSerializer(serializers.ModelSerializer):
    """ RetailerProduct serializer with minimum information - used in product-detail modal """
    class Meta:
        model = RetailerProduct
        fields = (
            'pk',
            'in_store_ppu',
            'units_available_in_store',
            'units_per_order',
            'location_address',
            'location_id',
            'company_name',
            'lead_time_ts'
        )


# class SupplierProductSerializer(serializers.ModelSerializer):
#     product = SerpyProduct()

#     class Meta:
#         model = SupplierProduct
#         fields = (
#             'pk',
#             'in_store_ppu',
#             'units_available_in_store',
#             'units_per_order',
#             'on_sale',
#             'sale_price',
#             'banner_item',
#             'product'
#         )


# class SupplierProductUpdateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = SupplierProduct
#         fields = (
#             'pk',
#             'in_store_ppu',
#             'units_available_in_store',
#             'units_per_order',
#             'publish_in_store_availability',
#             'publish_in_store_price',
#             'publish_online_price',
#             'sale_price',
#             'on_sale',
#             'banner_item',
#         )

#     def update(self, location, validated_data):
#         sup_prod_pk = validated_data.get('pk')
#         instance: SupplierProduct = location.priced_product.filter(pk=sup_prod_pk).first()
#         if not instance:
#             return
#         instance.in_store_ppu = validated_data.get('in_store_ppu', instance.in_store_ppu)
#         instance.units_available_in_store = validated_data.get(
#             'units_available_in_store',
#             instance.units_available_in_store
#             )
#         instance.units_per_order = validated_data.get('units_per_order', instance.units_per_order)
#         instance.publish_in_store_availability = validated_data.get(
#             'publish_in_store_availability', instance.publish_in_store_availability)
#         instance.publish_in_store_price = validated_data.get('publish_in_store_price', instance.publish_in_store_price)
#         instance.publish_online_price = validated_data.get('publish_online_price', instance.publish_online_price)
#         instance.save()
#         return
