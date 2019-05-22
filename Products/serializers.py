import serpy
from uuid import UUID
from rest_framework import serializers
from .models import Product, Manufacturer


class SerpyManufacturer(serpy.Serializer):
    pk = serpy.Field('id')
    label = serpy.Field()


class SerpyProduct(serpy.Serializer):
    # pk = serpy.Field()
    pk = serpy.MethodField()
    unit = serpy.Field()
    manufacturer_style = serpy.Field()
    manu_collection = serpy.Field()
    # for_sale_online = serpy.Field()
    for_sale_in_store = serpy.Field()
    name = serpy.Field()
    swatch_image = serpy.MethodField()
    manufacturer = SerpyManufacturer()
    lowest_price = serpy.MethodField()
    # average_price = serpy.Field()
    # average_rating = serpy.Field(call=True)
    # rating_count = serpy.Field(call=True)

    def get_lowest_price(self, prod_obj):
        return str(prod_obj.lowest_price)

    def get_swatch_image(self, prod_obj):
        return prod_obj.swatch_image.url

    def get_pk(self, prod_obj: Product):
        return str(prod_obj.bb_sku)


class ProductDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'unit',
            'actual_color',

            'manufacturer',
            'manufacturer_url',
            'manufacturer_sku',
            'manu_collection',
            'manufacturer_style',
            'manufacturer_name',
            'finish',

            'lowest_price',

            'room_scene',
            'swatch_image',
            'tiling_image',

        )

