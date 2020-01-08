""" Accounts.views.py """

import datetime
import os
import random
from django.shortcuts import redirect
from django.db import transaction
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .tasks import send_verification_email

from Profiles.models import BaseProfile, RetailerEmployeeProfile, ProEmployeeProfile
from .serializers import user_serializer

USER_TIMEOUT_MINUTES = .2


@api_view(['POST'])
@transaction.atomic()
def create_user(request):
    full_name = request.data.get('full_name', None)
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    user_type = request.data.get('user_type', None)
    is_pro = False
    is_supplier = False
    if user_type == 'is_pro':
        is_pro = True
    elif user_type == 'is_supplier':
        is_supplier = True
    user_model = get_user_model()
    user = None
    if not email or not password:
        return Response('Email and password required!', status=status.HTTP_400_BAD_REQUEST)
    user_check = user_model.objects.filter(email__iexact=email).first()
    if user_check:
        return Response(f'{email.lower()} already exists', status=status.HTTP_400_BAD_REQUEST)

    user = user_model.objects.create_user(
        email=email,
        full_name=full_name,
        password=password,
        is_active=True,
        is_pro=is_pro,
        is_supplier=is_supplier,
        date_registered=datetime.datetime.now()
    )

    if not user:
        return Response('No user created', status=status.HTTP_400_BAD_REQUEST)

    Token.objects.create(user=user)
    site = get_current_site(request).domain
    send_verification_email.delay(site, user.pk)
    return Response(user_serializer(user), status=status.HTTP_201_CREATED)


def activate(request, uidb64):
    user_model = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None
    if user is not None and user == Token.objects.get(user=user).user:
        user.email_verified = True
        user.date_confirmed = datetime.datetime.now()
        user.save()
        return redirect(settings.REDIRECT_URL)
    return HttpResponse('Activation link is invalid!')


@api_view(['POST'])
def custom_login(request):
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    user_model = get_user_model()

    if email is None or password is None:
        return Response('Email and Password Required!', status=status.HTTP_400_BAD_REQUEST)
    user = user_model.objects.filter(email__iexact=email).first()

    if not user:
        return Response('Invalid credentials', status=status.HTTP_400_BAD_REQUEST)
    if not check_password(password, user.password):
        return Response(f'Invalid password', status=status.HTTP_400_BAD_REQUEST)

    if not user.is_active:
        return Response(
            'Please check your inbox at ' + email + ' to verify your account',
            status=status.HTTP_400_BAD_REQUEST
            )

    if not user.profile:
        BaseProfile.objects.create_profile(user)

    if os.environ['DJANGO_SETTINGS_MODULE'] == 'config.settings.staging' and not user.is_staff:
        return Response("We're sorry this is for staff only", status=status.HTTP_403_FORBIDDEN)

    login(request, user)
    return Response(user_serializer(user), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_user(request):
    return Response(user_serializer(request.user), status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request):
    pass


@api_view(['GET'])
def get_demo_user(request, user_type='user', auth_type=None):

    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=USER_TIMEOUT_MINUTES)
    eligible_users = get_user_model().objects.filter(demo=True, last_seen__lt=time_threshold)

    auth_term = {}
    if auth_type in ('owner', 'admin'):
        auth_term[auth_type] = True
    else:
        auth_term['owner'] = False
        auth_term['admin'] = False

    user_type = user_type.lower()
    if user_type in ('retailer', 'retailers'):
        rpks = RetailerEmployeeProfile.objects.filter(**auth_term).values_list('user__pk', flat=True)
        eligible_users = eligible_users.filter(pk__in=rpks)
    elif user_type in ('pro', 'pros'):
        ppks = ProEmployeeProfile.objects.filter(**auth_term).values_list('user__pk', flat=True)
        eligible_users = eligible_users.filter(pk__in=ppks)
    else:
        eligible_users = eligible_users.filter(is_pro=False, is_supplier=False)


    pks = eligible_users.values_list('pk', flat=True)
    choice_pk = random.choice(pks)
    user = get_user_model().objects.get(pk=choice_pk)
    return Response(user_serializer(user), status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def custom_logout(request):
    request.user.auth_token.delete()
    logout(request)
    return Response(status=status.HTTP_200_OK)
