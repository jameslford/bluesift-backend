
# Products.serializers.py

from rest_framework import serializers
from .models import Product, Manufacturer, Image

class ManufacturerSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(default=0)
    enabled = serializers.BooleanField(default=False)
    class Meta:
        model = Manufacturer
        fields = ('id', 'name', 'products', 'count', 'enabled')

class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('image',)



class ProductSerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'image',

            'manufacturer',
            'manufacturer_name',

            'lowest_price',
            'units',

            'units',
            'prices',
            )

class ProductSemiDetailSerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    class Meta:
        model = Product
        fields = (
            'id',
            'name',

            'manufacturer',
            'manufacturer_name',
            'manufacturer_url',
            'manufacturer_sku',
            'manu_collection',
            'manufacturer_color',

            'lowest_price',
            'is_priced',
            'for_sale',
            'units',

            'image',
            'build_label',
            'material_label',
            'category_name',
            'material',
            'category_id',
            'look_label',

            'walls',
            'countertops',
            'cabinet_fronts',
            'floors',
            'shower_floors',
            'shower_walls',
            'exterior',
            'covered',
            'pool_linings',

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

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',

            'manufacturer',
            'manufacturer_name',
            'manufacturer_url',
            'manufacturer_sku',
            'manu_collection',
            'manufacturer_color',

            'lowest_price',
            'is_priced',
            'for_sale',
            'units',
            'prices',

            'image',
            'build_label',
            'material_label',
            'category_name',
            'material',
            'category_id',
            'look_label',

            'walls',
            'countertops',
            'cabinet_fronts',
            'floors',
            'shower_floors',
            'shower_walls',
            'exterior',
            'covered',
            'pool_linings',

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
