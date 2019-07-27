import serpy
from .models import Product
# from uuid import UUID
# from rest_framework import serializers


class SerpyManufacturer(serpy.Serializer):
    pk = serpy.Field('id')
    label = serpy.Field()


class SerpyProduct(serpy.Serializer):
    pk = serpy.MethodField()
    unit = serpy.Field()
    manufacturer_style = serpy.Field()
    manu_collection = serpy.Field()
    name = serpy.Field()
    swatch_image = serpy.MethodField()
    manufacturer = SerpyManufacturer()
    low_price = serpy.MethodField()
    # lowest_price = serpy.MethodField()

    # def get_lowest_price(self, prod_obj: Product):
    #     if not prod_obj.lowest_price:
    #         return None
    #     location_pk = self.label
    #     price = prod_obj.get_price(location_pk)
    #     if not price:
    #         return None
    #     return float(price)
    def get_low_price(self, prod_obj):
        if hasattr(prod_obj, 'low_price'):
            return prod_obj.low_price
        return None

    def get_swatch_image(self, prod_obj):
        if prod_obj.swatch_image:
            return prod_obj.swatch_image.url
        return None

    def get_pk(self, prod_obj: Product):
        return str(prod_obj.bb_sku)


# class ProductDetailSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Product
#         fields = (
#             'id',
#             'name',
#             'unit',
#             'actual_color',

#             'manufacturer',
#             'manufacturer_url',
#             'manufacturer_sku',
#             'manu_collection',
#             'manufacturer_style',
#             'manufacturer_name',
#             'finish',

#             'lowest_price',

#             'room_scene',
#             'swatch_image',
#             'tiling_image',
#         )
