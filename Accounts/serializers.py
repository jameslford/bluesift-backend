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
        'staff': user.staff,
        'admin': user.admin,
        'is_active': user.is_active,
        'email_verified': user.email_verified,
        'auth_token': str(auth_token)
    }
