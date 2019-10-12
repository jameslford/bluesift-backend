""" Profiles.serializers """
# import serpy
from rest_framework import serializers
from Accounts.serializers import UserSerializer
from .models import BaseProfile, RetailerEmployeeProfile, ProEmployeeProfile, ConsumerProfile


def serialize_profile(user):
    profile = user.get_profile()
    ret_dict = {
        'pk': profile.pk,
        'user': UserSerializer(user).data,
        'avatar': profile.avatar.url if profile.avatar else None
        }
    if not (user.is_pro or user.is_supplier):
        ret_dict['plan'] = profile.plan
        return ret_dict
    ret_dict['owner',] = profile.owner
    ret_dict['admin',] = profile.admin
    ret_dict['title'] = profile.title
    if user.is_supplier:
        ret_dict['locations_managed'] = profile.locations_managed()
    return ret_dict


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


# class BaseProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()

#     class Meta:
#         model = BaseProfile
#         fields = (
#             'pk',
#             'user'
#         )


# class ConsumerProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()

#     class Meta:
#         model = ConsumerProfile
#         fields = (
#             'pk',
#             'user',
#             'plan'
#         )


# class ProEmployeeProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()

#     class Meta:
#         model = ProEmployeeProfile
#         fields = (
#             'pk',
#             'user',
#             'owner',
#             'admin',
#             'title'
#         )


# class RetailerEmployeeShortSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = RetailerEmployeeProfile
#         fields = (
#             'pk',
#             'owner',
#             'name',
#             'admin',
#             'title'
#         )


# class RetailerEmployeeProfileSerializer(serpy.Serializers):
#     user = UserSerializer()
#     pk = serpy.Field()
#     user = serpy.Field()
#     owner = serpy.Field()
#     admin = serpy.Field()
#     title = serpy.Field()
