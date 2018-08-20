
# Products.serializers.py

from rest_framework import serializers
from .models import Product, Manufacturer



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
                    'for_sale',
                    'lowest_price',
                    'manufacturer', 
                    'prices',
                    'manufacturer_url',
                   )




class ManufacturerSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(default=0)
    enabled = serializers.BooleanField(default=False)
    class Meta:
        model = Manufacturer
        fields = ('id','name', 'products', 'count', 'enabled')


