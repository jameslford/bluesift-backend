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
                    'application', 
                    'product_type',
                    'prices',
                   )





class ProductTypeSerializer(serializers.ModelSerializer):
    enabled = serializers.BooleanField(default=False)
    class Meta:
        model = ProductType
        fields = ('material', 'unit', 'id', 'enabled')


class ApplicationAreaSerializer(serializers.ModelSerializer):
    enabled = serializers.BooleanField(default=False)
    class Meta:
        model = Application
        fields = ('id', 'area', 'enabled')

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ('id','name', 'products')