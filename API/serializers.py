# API.serializers.py

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from Products.models import Product, Manufacturer
from django.conf import settings
class ProductSerializer(serializers.ModelSerializer):

    manufacturer_name = serializers.SerializerMethodField('get_manu_name')
    class Meta:

        model = Product
        fields = ('manufacturer_name', 'manufacturer', 'name', 'image')

    def get_manu_name (self, obj):
        return obj.manufacturer.name

'''class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=20)

    def create_supllier(self, validated_data):
        
        user = settings.AUTH_USER_MODEL

        supplier = user.objects.create(
        email = validated_data['email'],
        first_name = validated_data['first_name'],
        last_name= validated_data['last_name'],
        password= validated_data['password'],
        is_supplier= True
    
        )
        return supplier


    class Meta:
        model = get_user_model()
        fields = ('email','first_name', 'last_name', 'password')'''
 


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(
                                    min_length=8, 
                                    max_length=32,
                                    required=True, 
                                    validators=[UniqueValidator(queryset=get_user_model().objects.all())]
                                    )
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    password = serializers.CharField(max_length=20, write_only=True)
    is_supplier = serializers.BooleanField(default=False, required=False)
    id = serializers.ReadOnlyField()
    
   


class CreateUserSerializer(UserSerializer):
    def create(self, validated_data):
        user = get_user_model()
        return user.objects.create(**validated_data)

