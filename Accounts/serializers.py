from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import User


def user_serializer(user: User):

    auth_token = Token.objects.get_or_create(user=user)[0]
    return {
        'pk': user.pk,
        'email': user.email,
        'full_name': user.full_name,
        'get_first_name': user.get_first_name(),
        'get_full_name': user.get_full_name(),
        'get_initials': user.get_initials(),
        'is_supplier': user.is_supplier,
        'demo': user.demo,
        'is_pro': user.is_pro,
        'staff': user.staff,
        'admin': user.admin,
        'is_active': user.is_active,
        'email_verified': user.email_verified,
        'auth_token': str(auth_token)
    }

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = (
#             'pk',
#             'email',
#             'full_name',
#             'get_first_name',
#             'get_full_name',
#             'get_initials',
#             'is_supplier',
#             'demo',
#             'is_pro',
#             'staff',
#             'admin',
#             'is_active',
#             'email_verified',
#             'auth_token'
#         )


# class UserResponseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = (
#             'pk',
#             'email',
#             'get_first_name',
#             'is_supplier',
#             'is_pro',
#             'auth_token',
#             'is_admin'
#             )


# class CreateUserSerializer(UserSerializer):
#     def create(self, validated_data):
#         user = get_user_model()
#         return user.objects.create(**validated_data)


# class CreateSupplierSerializer(UserSerializer):
#     company_name = serializers.CharField(max_length=120, required=True)
#     phone_number = serializers.IntegerField(required=True)


# class LoginSerializer(serializers.Serializer):
#     email = serializers.CharField(max_length=50)
#     password = serializers.CharField(max_length=20, write_only=True)
