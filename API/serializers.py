# API.serializers.py

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from Products.models import Product, Manufacturer, SupplierProduct, Application, ProductType
from Libraries.models import UserLibrary
from django.conf import settings


 
class UserSerializer(serializers.Serializer):
    email                   = serializers.EmailField(
                                    min_length=8, 
                                    max_length=32,
                                    #required=True, 
                                    validators=[UniqueValidator(queryset=get_user_model().objects.all())]
                                    )
    first_name              = serializers.CharField(max_length=100, required=False)
    last_name               = serializers.CharField(max_length=100, required=False)
    password                = serializers.CharField(max_length=20, write_only=True)
    is_supplier             = serializers.BooleanField(default=False, required=False)
    id                      = serializers.ReadOnlyField()
    
   


class CreateUserSerializer(UserSerializer):
    def create(self, validated_data):
        user = get_user_model()
        return user.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    password                = serializers.CharField(max_length=60)
    email                   = serializers.CharField(max_length=60)
  
class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key',)


class ProductSerializer(serializers.ModelSerializer):

    manufacturer_name       = serializers.SerializerMethodField('get_manu_name')

    class Meta:
        model = Product
        fields = (
                    'id',
                    'manufacturer_name', 
                    'manufacturer', 
                    'name', 
                    'image',
                    'application', 
                    'product_type',
                    'is_priced',
                    'get_units',
                    'get_suppliers',
                   )

    def get_manu_name (self, obj):
        return obj.manufacturer.name



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
      
class UserLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLibrary
        fields = ('owner', 'name', 'products')
        