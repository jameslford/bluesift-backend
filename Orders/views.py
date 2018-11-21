from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from Carts.models import Cart



@api_view(['GET'])
def checkout_permission(request, pk=None):
    user = request.user
    if not user.is_authenticated:
        return Response('login')
    if not pk:
        return Response('invalid')
    if not Cart.objects.filter(id=pk).first():
        return Response('invalid')
    cart_obj = Cart.objects.get(id=pk)
    if cart_obj.item_count() < 1:
        return Response('invalid')
    if cart_obj.user != request.user:
        return Response('Danger')
    return Response('valid')