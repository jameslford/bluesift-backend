# API.views.py

from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from .serializers import ProductSerializer, CreateUserSerializer
from Products.models import Product 
from Libraries.models import Library

from django.conf import settings
#from config.urls import urlpatterns

class ProductList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serialized = ProductSerializer(products, many=True)
        return Response(serialized.data)
        
'''class CreateUser(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]'''


@api_view(['POST'])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        if user.is_supplier == True:
            lib_name = user.get_first_name() + "'s Library"
            Library.objects.create(owner=user, name=lib_name)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

