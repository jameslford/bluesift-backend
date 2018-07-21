# Accounts.views.py

from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model, login, authenticate
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site

import datetime




from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import(
                        CreateSupplierSerializer,
                        CreateUserSerializer,
                        UserSerializer,
                        LoginSerializer,
                        TokenSerializer
                        )

from Profiles.models import(
                            CompanyAccount,
                            CompanyShippingLocation,
                            CustomerProfile,
                            CustomerProject
                            ) 



                    

@api_view(['POST'])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        lib_name = user.get_first_name() + "'s Library"
        user.date_registered = datetime.datetime.now()

        current_site = get_current_site(request)
        mail_subject = 'Activate your Building Book account.'
        message = render_to_string('acc_activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': Token.objects.create(user=user)
        })
        to_email = user.email 
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        profile = CustomerProfile.objects.create(user=user)
        CustomerProject.objects.create(owner=profile, nickname='First Project')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def create_supplier(request):

    userModel = get_user_model()
    email = request.POST.get('email')
    password = request.POST.get('Spassword')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    company_name = request.POST.get('company_name')
    phone_number = request.POST.get('phone_number')
    supplier = userModel.objects.create(
                                        email=email, 
                                        password=password, 
                                        first_name=first_name, 
                                        last_name=last_name, 
                                        is_supplier=True, 
                                        is_active=False
                                        )
    supplier.date_registered = datetime.datetime.now()
    current_site = get_current_site(request)
    mail_subject = 'Activate your Building Book account.'
    message = render_to_string('acc_activate_email.html', {
        'user': supplier,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(supplier.pk)).decode(),
        'token': Token.objects.create(user=supplier)
    })
    to_email = supplier.email 
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
    company = CompanyAccount.objects.create(name=company_name, phone_number=phone_number, account_owner=supplier)
    CompanyShippingLocation.objects.create(company_account=company, nickname='Main Location')
    serializer = UserSerializer(supplier)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
        

def activate(request, uidb64, token):
    userModel = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = userModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, userModel.DoesNotExist):
        user = None
    if user is not None and user == Token.objects.get(user=user).user :
        user.is_active = True
        user.date_confirmed = datetime.datetime.now()
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return Response('Activation link is invalid!')

@api_view(['POST'])
def get_token(request):
    serializer = LoginSerializer(data=request.data)
    userModel = get_user_model()
    if serializer.is_valid():
        email = serializer.data['email']
        password = serializer.data['password']
        try:
            user = userModel.objects.get(email=email)
        except(TypeError, ValueError, OverflowError, userModel.DoesNotExist):
            user = None
        if user:
            if password == user.password:
                if user.is_active == True:
                    token = Token.objects.get(user=user)
                    sToken = TokenSerializer(instance=token)
                    sUser = UserSerializer(instance=user)
                    content = {
                        'key' : sToken.data['key'],
                        'email' : sUser.data['email'],
                        'first_name' : sUser.data['first_name'],
                        'last_name' : sUser.data['last_name'],
                        'is_supplier' : sUser.data['is_supplier'],
                        'id' : sUser.data['id'],
                    }
                    return Response(content)
                return Response("please verify your account")
            return Response("incorrect password")
        return Response("no user found")
    return Response(serializer.errors)
