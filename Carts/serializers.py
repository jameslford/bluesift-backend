from rest_framework import serializers
from Profiles.serializers import SupplierProductSerializer
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product = SupplierProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ('products', 'quantity')

class CartSerializer(serializers.ModelSerializer):
    cartitem_set = CartItemSerializer(read_only=True, many=True)
    class Meta:
        model = Cart
        fields = ('cartitem_set',)
