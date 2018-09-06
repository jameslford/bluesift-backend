
# Products.serializers.py

from rest_framework import serializers
from .models import Product, Manufacturer



class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'manufacturer',
            'manufacturer_name',
            'manufacturer_url',
            'lowest_price',
            'is_priced',
            'for_sale',
            'image',
            'build',
            'material',
            'walls',
            'countertops',
            'floors',
            'shower_floors',
            'shower_walls',
            'exterior',
            'covered',
            'pool_linings',
            'material',
            'category_name',
            'category_id',
            'units',
            'prices',
            'manufacturer_url',
            )




class ManufacturerSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(default=0)
    enabled = serializers.BooleanField(default=False)
    class Meta:
        model = Manufacturer
        fields = ('id', 'name', 'products', 'count', 'enabled')

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
            'lowest_price',
            'is_priced',
            'for_sale',
            'image',
            'build',
            'material',
            'walls',
            'countertops',
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
            'image_2',
            'residential_warranty',
            'commercial_warranty',
            'material',
            'category_name',
            'category_id',
            'units',
            'prices',
            'manufacturer_url',
            'description',
            'look_label',
            'size'
        )
