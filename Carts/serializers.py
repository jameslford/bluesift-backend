from rest_framework import serializers
from Profiles.serializers import SupplierProductSerializer
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product = SupplierProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = (
            'product',
            'quantity',
            'id',
            'total'
            )

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(read_only=True, many=True)
    class Meta:
        model = Cart
        fields = (
            'items',
            'id',
            'add_subtotal',
            'add_total'
            )
