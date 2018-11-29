
# Products.serializers.py

from rest_framework import serializers
from .models import(
    Product,
    Manufacturer,
    Image,
    Build,
    Material,
    Category,
    Look
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
    image = ImageSerializer()
    manufacturer = ManufacturerSerializer()
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'image',
            'manufacturer',
            'lowest_price',
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

            'image',
            'build_label',
            'material_label',
            'category_name',
            'material',
            'finish_label',
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
