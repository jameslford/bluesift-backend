""" Profiles.serializers """
from rest_framework import serializers
from Accounts.serializers import UserSerializer
from Plans.serializers import PlanSerializer


def serialize_profile(user):
    profile = user.get_profile()
    ret_dict = {
        'pk': profile.pk,
        'user': UserSerializer(user).data,
        'avatar': profile.avatar.url if profile.avatar else None
        }
    if not (user.is_pro or user.is_supplier):
        ret_dict['plan'] = PlanSerializer(profile.plan).data
        return ret_dict
    ret_dict['owner'] = profile.owner
    ret_dict['admin'] = profile.admin
    ret_dict['title'] = profile.title
    if user.is_supplier:
        ret_dict['locations_managed'] = profile.locations_managed()
    return ret_dict
