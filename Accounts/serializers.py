from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.conf import settings
from django.contrib.auth import get_user_model


class UserSerializer(serializers.Serializer):
    email                   = serializers.EmailField(
                                    min_length=8, 
                                    max_length=32,
                                    required=True, 
                                    validators=[UniqueValidator(queryset=get_user_model().objects.all())]
                                    )
    first_name              = serializers.CharField(max_length=100, required=False)
    last_name               = serializers.CharField(max_length=100, required=False)
    password                = serializers.CharField(max_length=20, write_only=True)
    is_supplier             = serializers.BooleanField(default=False, required=False)
    id                      = serializers.ReadOnlyField()

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'get_first_name',
            'last_name',
            'is_supplier',
            'auth_token'
            )


class CreateUserSerializer(UserSerializer):
    def create(self, validated_data):
        user = get_user_model()
        return user.objects.create(**validated_data)

class CreateSupplierSerializer(UserSerializer):
    company_name            = serializers.CharField(max_length=120, required=True)
    phone_number            = serializers.IntegerField(required=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=20, write_only=True)
    

  