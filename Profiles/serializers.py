import serpy
from rest_framework import serializers
from Accounts.serializers import UserSerializer
from Groups.serializers import ProListSerializer, RetailerCompanyHeaderSerializer
from .models import BaseProfile, RetailerEmployeeProfile, ProEmployeeProfile, ConsumerProfile


class BaseProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = BaseProfile
        fields = (
            'pk',
            'user'
        )


class ConsumerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ConsumerProfile
        fields = (
            'pk',
            'user',
            'plan'
        )


class ProEmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    company = ProListSerializer()

    class Meta:
        model = ProEmployeeProfile
        fields = (
            'pk',
            'user',
            'company',
            'owner',
            'admin',
            'title'
        )


class RetailerEmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    company = RetailerCompanyHeaderSerializer()

    class Meta:
        model = RetailerEmployeeProfile
        fields = (
            'pk',
            'user',
            'company',
            'owner',
            'admin',
            'title'
        )







# import base64
# from rest_framework import serializers
# from django.core.files.base import ContentFile
# from Addresses.serializers import AddressSerializer, AddressUpdateSerializer
# from Addresses.models import Address, Zipcode
# from django.contrib.postgres.search import SearchVector
# from Products.serializers import SerpyProduct
# from .models import (
#     CompanyAccount,
#     CompanyShippingLocation,
#     EmployeeProfile,
#     SupplierProduct,
#     )





# class EmployeeProfileSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = EmployeeProfile
#         fields = (
#             'pk',
#             'title',
#             'name',
#             'email',
#             'company_account_owner',
#             'company_account_admin',
#         )





