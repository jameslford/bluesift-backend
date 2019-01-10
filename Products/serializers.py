
# Products.serializers.py

from rest_framework import serializers
from .models import (
    Product,
    Manufacturer,
    Image
    )


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ('id', 'label')


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('image',)


class ProductSerializer(serializers.ModelSerializer):
    swatch_image = ImageSerializer()
    # tiling_image = ImageSerializer()
    manufacturer = ManufacturerSerializer()

    class Meta:
        model = Product
        fields = (
            'id',
            'bb_sku',
            'name',
            'actual_color',
            # 'label_color',
            'swatch_image',
            'tiling_image',
            'manufacturer',
            'lowest_price',
            )


class ProductDetailSerializer(serializers.ModelSerializer):
    room_scene = ImageSerializer()
    swatch_image = ImageSerializer()
    tiling_image = ImageSerializer()

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
