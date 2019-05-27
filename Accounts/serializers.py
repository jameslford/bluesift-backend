from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.conf import settings
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'pk',
            'email',
            'get_first_name',
            'password',
            'is_supplier',
            'staff',
            'admin',
            'is_active',
            'auth_token'
        )


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'pk'
            'email',
            'get_first_name',
            'is_supplier',
            'auth_token',
            'is_admin'
            )


class CreateUserSerializer(UserSerializer):
    def create(self, validated_data):
        user = get_user_model()
        return user.objects.create(**validated_data)


class CreateSupplierSerializer(UserSerializer):
    company_name = serializers.CharField(max_length=120, required=True)
    phone_number = serializers.IntegerField(required=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=20, write_only=True)
