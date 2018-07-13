# API.views.py
import datetime
from rest_framework.renderers import JSONRenderer

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .serializers import ( 
                            ProductSerializer, 
                            CreateUserSerializer, 
                            UserSerializer, 
                            LoginSerializer, 
                            TokenSerializer, 
                            ApplicationAreaSerializer,
                            ProductTypeSerializer,
                            )
from Products.models import ( 
                            Product, 
                            Application,
                            ProductType,
                            )

from Libraries.models import UserLibrary, SupplierLibrary

#from config.urls import urlpatterns

class ProductList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        application_areas = Application.objects.all()
        product_types = ProductType.objects.all()

        p_serialized = ProductSerializer(products, many=True)
        a_serialized = ApplicationAreaSerializer(application_areas, many=True)
        pt_serialized = ProductTypeSerializer(product_types, many=True) 
               
        return Response({
                        "areas" : a_serialized.data, 
                        "product_types": pt_serialized.data, 
                        "products": p_serialized.data
                        })
        


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
        if user.is_supplier == True:
            SupplierLibrary.objects.create(owner=user, name=lib_name)
        else:
            UserLibrary.objects.create(owner=user, name=lib_name)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        #return HttpResponse('Thank you for your email confirmation. Now you can login to your account')
    else:
        return HttpResponse('Activation link is invalid!')

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
                return HttpResponse("please verify your account")
            return HttpResponse("incorrect password")
        return HttpResponse("no user found")
    return Response(serializer.errors)


@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data['email']})
    return Response({"message": "Hello, world!"})


# class StructureView(APIView):
#     def get(self, request, format=none):
#         application_areas = Application.objects.all()
#         serialized = ApplicationAreaSerializer(application_areas, many=True)
#         return Response({"areas" : serialized.data })