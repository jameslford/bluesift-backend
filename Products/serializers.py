
# Products.serializers.py

from rest_framework import serializers
from .models import Product, Manufacturer, Application, ProductType



class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
                    'id',
                    'manufacturer_name', 
                    'name', 
                    'image',
                    'material',
                    'units',
                    'is_priced',
                    'lowest_price',
                    'manufacturer', 
                    'product_type',
                    'prices',
                    'manufacturer_url',
                    'application', 
                   )





class ProductTypeSerializer(serializers.ModelSerializer):
    enabled = serializers.BooleanField(default=False)
    count = serializers.IntegerField(default=0)
    class Meta:
        model = ProductType
        fields = ('material', 'unit', 'id', 'enabled', 'count')


class ApplicationAreaSerializer(serializers.ModelSerializer):
    enabled = serializers.BooleanField(default=False)
    count = serializers.IntegerField(default=0)
    class Meta:
        model = Application
        fields = ('id', 'area', 'enabled', 'count')

class ManufacturerSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(default=0)
    enabled = serializers.BooleanField(default=False)
    class Meta:
        model = Manufacturer
        fields = ('id','name', 'products', 'count', 'enabled')


