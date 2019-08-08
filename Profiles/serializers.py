""" Profiles.serializers """
import serpy
from rest_framework import serializers
from Accounts.serializers import UserSerializer
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

    class Meta:
        model = ProEmployeeProfile
        fields = (
            'pk',
            'user',
            'owner',
            'admin',
            'title'
        )


class RetailerEmployeeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = RetailerEmployeeProfile
        fields = (
            'pk',
            'owner',
            'name',
            'admin',
            'title'
        )


class RetailerEmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = RetailerEmployeeProfile
        fields = (
            'pk',
            'user',
            'owner',
            'admin',
            'title',
            'locations_managed'
        )


# class RetailerEmployeeProfileSerializer(serpy.Serializers):
#     user = UserSerializer()
#     pk = serpy.Field()
#     user = serpy.Field()
#     owner = serpy.Field()
#     admin = serpy.Field()
#     title = serpy.Field()


