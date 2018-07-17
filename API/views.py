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
# , is_priced=False, property_type=None, application_type=None

@api_view(['GET'])
def product_list(request):

    # parse request
    is_priced = request.GET.get('is_priced', 'False')
    product_type = request.GET.get('product_type', 'All')
    application_type = request.GET.get('application_type', '0')
    manufacturer = request.GET.get('manufacturer', 'All')

    # structure filter objects
    filter_content = {
        "is_priced" : is_priced,
        "product_type" : product_type,
        "application_type" : application_type,
        "manufacturer" : manufacturer,
    }

    # filter products
    pTyped_products = parse_pt(product_type)
    aTyped_products = parse_at(application_type, pTyped_products)
    mTyped_products = parse_manufacturer(manufacturer, aTyped_products)
    filtered_products = parse_priced(is_priced, mTyped_products)
    products_serialized = ProductSerializer(filtered_products, many=True)

    # filter application types
    application_types = Application.objects.all()
    app_types_serialized = ApplicationAreaSerializer(application_types, many=True)
    active_ats = active_at(filtered_products)
    refined_ats = app_type_enabler(active_ats, app_types_serialized)

    # filter product types
    product_types = ProductType.objects.all()
    prod_types_seriallized = ProductTypeSerializer(product_types, many=True)
    active_pts = active_pt(filtered_products)
    refined_pts = app_type_enabler(active_pts, prod_types_seriallized)

    



    return Response({
                    "filter" : filter_content,
                    "application_types": refined_ats.data,
                    "product_types": refined_pts.data,
                    "products": products_serialized.data
                    })
    



def parse_pt(product_type):
    products = Product.objects.all()
    if product_type == 'All':
        return products
    else:
        return products.filter(product_type=product_type)

def parse_at(application_type, products):
    if application_type == '0':
        return products
    else:
        return products.filter(application=application_type)

def parse_manufacturer(manufacturer, products):
    if manufacturer == 'All':
        return products
    else:
        return products.filter(manufacturer=manufacturer)


def parse_priced(is_priced, products):
    if is_priced == 'true':   
        prods = []
        for product in products:
            if product.is_priced() == True:
                prods.append(product)
                return prods
    else:
        return products


def active_at(products):
    if products:
        actives = []
        for product in products:
            ats = product.application.all()
            for at in ats:
                actives.append(at.id)
        active = set(actives)
        return active
    else:
        return


def active_pt(products):
    if products:
        actives = []
        for product in products:
            if product.product_type:
                pt = product.product_type
                actives.append(pt.id)
        active = set(actives)
        return active
    else:
        return


def app_type_enabler(active_ids, serialized_app_types):
    for app_type in serialized_app_types.data:
        if app_type['id'] in active_ids:
            app_type['enabled'] = True
    return serialized_app_types




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


