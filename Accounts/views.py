""" Accounts.views.py """

import datetime
import os
from django.shortcuts import redirect
from django.db import transaction
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from Profiles.models import BaseProfile
from .serializers import (
    UserResponseSerializer,
    )


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
    hashed_password = make_password(password)

    user = user_model.objects.create_user(
        email=email,
        full_name=full_name,
        password=hashed_password,
        is_pro=is_pro,
        is_supplier=is_supplier,
        date_registered=datetime.datetime.now()
    )

    if not user:
        return Response('No user created', status=status.HTTP_400_BAD_REQUEST)

    token = Token.objects.get_or_create(user=user)

    message = render_to_string('acc_activate_email.html', {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token
    })

    email_obj = EmailMessage(
        subject="Activate your Buildbook account",
        body=message,
        from_email='jford@bluesift.com',
        to=[user.email]
        )
    email_obj.send()

    return Response(UserResponseSerializer(user).data, status=status.HTTP_201_CREATED)


def activate(request, uidb64):
    user_model = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None
    if user is not None and user == Token.objects.get(user=user).user:
        user.is_active = True
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

    if not user and check_password(password, user.password):
        return Response('Invalid Credentials', status=status.HTTP_400_BAD_REQUEST)

    if not user.is_active:
        return Response(
            'Please check your inbox at ' + email + ' to verify your account',
            status=status.HTTP_400_BAD_REQUEST
            )

    if not user.get_profile():
        if user.is_pro or user.is_supplier:
            return Response('Profile needed', status=status.HTTP_428_PRECONDITION_REQUIRED)
        BaseProfile.objects.create_profile(user)

    if os.environ['DJANGO_SETTINGS_MODULE'] == 'config.settings.staging' and not user.is_staff:
        return Response("We're sorry this is for staff only", status=status.HTTP_403_FORBIDDEN)

    return Response(UserResponseSerializer(user).data, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request):
    pass
