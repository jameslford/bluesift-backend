from rest_framework import serializers
from Products.serializers import SerpyProduct
from UserProducts.models import SupplierProduct


class SupplierProductSerializer(serializers.ModelSerializer):
    product = SerpyProduct()

    class Meta:
        model = SupplierProduct
        fields = (
            'pk',
            'in_store_ppu',
            'units_available_in_store',
            'units_per_order',
            'on_sale',
            'sale_price',
            'banner_item',
            'product'
        )


class SupplierProductUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupplierProduct
        fields = (
            'pk',
            'in_store_ppu',
            'units_available_in_store',
            'units_per_order',
            'publish_in_store_availability',
            'publish_in_store_price',
            'publish_online_price',
            'sale_price',
            'on_sale',
            'banner_item',
        )

    def update(self, location, validated_data):
        sup_prod_pk = validated_data.get('pk')
        instance: SupplierProduct = location.priced_product.filter(pk=sup_prod_pk).first()
        if not instance:
            return
        instance.in_store_ppu = validated_data.get('in_store_ppu', instance.in_store_ppu)
        instance.units_available_in_store = validated_data.get(
            'units_available_in_store',
            instance.units_available_in_store
            )
        instance.units_per_order = validated_data.get('units_per_order', instance.units_per_order)
        instance.publish_in_store_availability = validated_data.get(
            'publish_in_store_availability', instance.publish_in_store_availability)
        instance.publish_in_store_price = validated_data.get('publish_in_store_price', instance.publish_in_store_price)
        instance.publish_online_price = validated_data.get('publish_online_price', instance.publish_online_price)
        instance.save()
        return


class SupplierProductMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupplierProduct
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
