from rest_framework import serializers
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
            'is_pro',
            'staff',
            'admin',
            'is_active',
            'email_verified',
            'auth_token'
        )


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'pk',
            'email',
            'get_first_name',
            'is_supplier',
            'is_pro',
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


# class LoginSerializer(serializers.Serializer):
#     email = serializers.CharField(max_length=50)
#     password = serializers.CharField(max_length=20, write_only=True)
