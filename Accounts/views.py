# Accounts.views.py

import datetime
from django.shortcuts import redirect
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import (
    UserSerializer,
    UserResponseSerializer,
    )

from Profiles.models import CompanyAccount, EmployeeProfile
from Profiles.serializers import CompanyAccountSerializer
from CustomerProfiles.models import CustomerProfile, CustomerProject
from CustomerProfiles.serializers import CustomerProfileSerializer


@api_view(['POST'])
def create_user(request):
    supplier_str = request.data.get('is_supplier', False)
    is_supplier = True if supplier_str == 'true' else False
    full_name = request.data.get('full_name', None)
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    company_account_dict = request.data.get('company_account', None)
    company_name = None
    company_phone = None
    if company_account_dict:
        company_name = company_account_dict.get('company_name', None)
        company_phone = company_account_dict.get('phone_number', None)
    user_model = get_user_model()
    user = None
    if not email or not password:
        return Response('Email and password required!', status=status.HTTP_400_BAD_REQUEST)
    hashed_password = make_password(password)

    try:
        user = user_model.objects.create(
            full_name=full_name,
            email=email,
            password=hashed_password,
            is_supplier=is_supplier,
            date_registered=datetime.datetime.now()
            )
    except IntegrityError as err:
        if 'unique constraint' in err.args[0]:
            return Response('User already exist', status=status.HTTP_400_BAD_REQUEST)
        return Response('User exist', status=status.HTTP_400_BAD_REQUEST)

    if not user:
        return Response('No user created', status=status.HTTP_400_BAD_REQUEST)

    if user.is_supplier:
        company, created = CompanyAccount.objects.get_or_create(name=company_name)
        if not created:
            return Response(
                    'Company Account already exist. Please contact administrator for access',
                    status=status.HTTP_401_UNAUTHORIZED
                )
        company.phone_number = company_phone
        company.save()

        EmployeeProfile.objects.create(user=user, company_account=company)

    else:
        profile = CustomerProfile.objects.create(user=user)
        CustomerProject.objects.create(owner=profile, nickname='First Project')

        current_site = get_current_site(request)
        message = get_message(user, current_site)
        to_email = user.email
        email_obj = EmailMessage(
            subject="Activate your Buildbook account",
            body=message,
            to=[to_email]
            )
        email_obj.send()

    return Response('Created', status=status.HTTP_201_CREATED)


def get_message(user, current_site):
    message = render_to_string('acc_activate_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': Token.objects.create(user=user)
    })
    return message


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
        if user.is_supplier:
            user_company = user.employee_profile.company_account

            user_company.email_verified = True
            user_company.save()

            user.employee_profile.company_account_owner = True
            user.employee_profile.save()

        return redirect(settings.REDIRECT_URL)
    return HttpResponse('Activation link is invalid!')


@api_view(['POST'])
def custom_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user_model = get_user_model()

    if email is None or password is None:
        return Response('Email and Password Required!', status=status.HTTP_400_BAD_REQUEST)
    try:
        user = user_model.objects.get(email=email)
    except user_model.DoesNotExist:
        user = None

    if not user:
        return Response('Invalid Credentials', status=status.HTTP_404_NOT_FOUND)

    if not check_password(password, user.password):
        return Response('Invalid Credentials password', status=status.HTTP_404_NOT_FOUND)

    if not user.is_active:
        return Response(
            'Please check your inbox at ' + email + ' to verify your account',
            status=status.HTTP_400_BAD_REQUEST
            )

    serialized_user = UserResponseSerializer(user)
    return Response(serialized_user.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_details(request):
    user = request.user
    serialized_user = UserSerializer(user)
    if user.is_supplier:
        account = CompanyAccount.objects.get_or_create(account_owner=user)
        serialized_account = CompanyAccountSerializer(account)
    else:
        account = CustomerProfile.objects.get_or_create(user=user)
        serialized_account = CustomerProfileSerializer(user=user)

    context = {
        'user': serialized_user.data,
        'account': serialized_account.data
    }
    return Response(context)
