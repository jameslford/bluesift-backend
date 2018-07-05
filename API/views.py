# API.views.py
import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .serializers import ProductSerializer, CreateUserSerializer, UserSerializer
from Products.models import Product 
from Libraries.models import UserLibrary, SupplierLibrary

#from config.urls import urlpatterns

class ProductList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serialized = ProductSerializer(products, many=True)
        return Response({"products": serialized.data})
        


@api_view(['POST'])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    
    #serializer = CreateUserSerializer()

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








    

'''
{
    "email":"john@gmail.com",
    "password":"blahblah"
}

'''