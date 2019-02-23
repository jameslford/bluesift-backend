# Products.serializers.py

import serpy
from rest_framework import serializers
from .models import (
    Product,
    Color,
    Finish,
    Manufacturer,
    Material,
    Image
    )


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ('id', 'label')


class SerpyManufacturer(serpy.Serializer):
    pk = serpy.Field('id')
    label = serpy.Field()


class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = ('id', 'label')


class SerpyMasterial(serpy.Serializer):
    pk = serpy.Field('id')
    label = serpy.Field()


class FinishSerializer(serializers.ModelSerializer):

    class Meta:
        model = Finish
        fields = ('id', 'label')


class SerpyFinish(serpy.Serializer):
    pk = serpy.Field('id')
    label = serpy.Field()


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('image',)


class SerpyImage(serpy.Serializer):
    pk = serpy.Field('id')
    image = serpy.Field()


class ColorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Color
        fields = ('label')


class SerpyColor(serpy.Serializer):
    label = serpy.Field()


class ProductSerializer(serializers.ModelSerializer):
    swatch_image = ImageSerializer()
    manufacturer = ManufacturerSerializer()
    # tiling_image = ImageSerializer()
    # label_color = ColorSerializer()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'swatch_image',
            'manufacturer',
            'lowest_price',
            # 'bb_sku',
            # 'manufacturer_color',
            # 'manu_collection',
            # 'for_sale_online',
            # 'for_sale_in_store',
            # 'size',
            # 'actual_color',
            # 'label_color',
            # 'tiling_image',
            )


class SerpyProduct(serpy.Serializer):
    pk = serpy.Field('id')
    bb_sku = serpy.Field()
    manufacturer_color = serpy.Field()
    manu_collection = serpy.Field()
    for_sale_online = serpy.Field()
    for_sale_in_store = serpy.Field()
    name = serpy.Field()
    swatch_image = serpy.MethodField()
    manufacturer = SerpyManufacturer()
    lowest_price = serpy.Field()

    def get_swatch_image(self, prod_obj):
        return prod_obj.swatch_image.image.url


class ProductSerializerforSupplier(serializers.ModelSerializer):
    swatch_image = ImageSerializer()
    manufacturer = ManufacturerSerializer()
    material = MaterialSerializer()

    class Meta:
        model = Product
        fields = (
            'pk',
            'manufacturer_color',
            'manu_collection',
            'material',
            'size',
            'name',
            'swatch_image',
            'manufacturer',
            'lowest_price',
            )


class ProductDetailSerializer(serializers.ModelSerializer):
    room_scene = ImageSerializer(required=False)
    swatch_image = ImageSerializer()
    tiling_image = ImageSerializer(required=False)
    finish = FinishSerializer(required=False)
    material = MaterialSerializer(required=False)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'actual_color',

            'manufacturer',
            'manufacturer_url',
            'manufacturer_sku',
            'manu_collection',
            'manufacturer_color',
            'manufacturer_name',
            'finish',

            'lowest_price',

            'room_scene',
            'swatch_image',
            'tiling_image',
            'material',

            'walls',
            'countertops',
            'cabinet_fronts',
            'floors',
            'shower_floors',
            'shower_walls',
            'exterior_walls',
            'exterior_floors',
            'covered_walls',
            'covered_floors',
            'pool_linings',
            'locations',

            'lrv',
            'cof',
            'look',
            'width',
            'thickness',
            'length',
            'residential_warranty',
            'commercial_warranty',
            'size'
        )
