from rest_framework.authtoken.models import Token
from Profiles.models import BaseProfile, ConsumerProfile, SupplierEmployeeProfile
from .models import User


def user_serializer(user: User):

    auth_token = Token.objects.get_or_create(user=user)[0]
    profile = BaseProfile.subclasses.get_subclass(user=user)
    ret_dict = {
        'pk': user.pk,
        'email': user.email,
        'full_name': user.full_name,
        'get_first_name': user.get_first_name(),
        'get_full_name': user.get_full_name(),
        'get_initials': user.get_initials(),
        'is_supplier': user.is_supplier,
        'current_zipcode': user.current_zipcode.code if user.current_zipcode else None,
        'lat': user.current_zipcode.centroid.lat if user.current_zipcode else None,
        'lng': user.current_zipcode.centroid.lng if user.current_zipcode else None,
        'demo': user.demo,
        'staff': user.staff,
        'admin': user.admin,
        'avatar' : profile.avatar.url if profile.avatar else None,
        'email': user.email,
        'is_active': user.is_active,
        'email_verified': user.email_verified,
        'auth_token': str(auth_token)
        }
    if isinstance(profile, ConsumerProfile):
        ret_dict.update({
        'plan' : profile.plan,
        'phone_number' : profile.phone_number
        })
    elif isinstance(profile, SupplierEmployeeProfile):
        ret_dict.update({
        'company_owner' : profile.company_owner,
        'company_admin' : profile.company_admin,
        'title': profile.title,
        })
