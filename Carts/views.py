from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from UserProducts.models import SupplierProduct
from .models import Cart, CartItem
from .serializers import CartSerializer


def new_or_get(request, pk):
    user = request.user
    if not user.is_authenticated:
        if pk:
            cart_obj = Cart.objects.get_or_create(id=pk)[0]
            return cart_obj
        cart_obj = Cart.objects.create()
        return cart_obj
    if not pk:
        if user.cart:
            cart_obj = user.cart
            return cart_obj
        cart_obj = Cart.objects.create(user=user)
        return cart_obj
    if user.cart.id == pk:
        return user.cart
    temp_cart = Cart.objects.get_or_create(id=pk)[0]
    temp_items = [item for item in temp_cart.items.all()]
    cart_obj = user.cart
    for item in temp_items:
        item.cart = cart_obj
        item.save()
    return cart_obj


@api_view(['POST'])
def add_to_cart(request, pk=None):
    supplier_product_id = request.POST.get('supplier_product_id', None)
    qty = request.POST.get('qty')
    qty = int(qty)
    prod_obj = None

    if supplier_product_id:
        supplier_product_id = int(supplier_product_id)
        try:
            prod_obj = SupplierProduct.objects.get(id=supplier_product_id)
        except SupplierProduct.DoesNotExist:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)

    cart_obj = new_or_get(request, pk)

    for item in cart_obj.items.all():
        if item.product == prod_obj:
            qty = qty + item.quantity
            item.delete()
    units_av = prod_obj.units_available
    if units_av < qty:
        item = CartItem.objects.create(cart=cart_obj, product=prod_obj, quantity=units_av)
        return Response(
            'Order quantity is greater than units available',
            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )
    item = CartItem.objects.create(cart=cart_obj, product=prod_obj, quantity=qty)
    context = {
        'cart_id': cart_obj.id,
        'prod_id': prod_obj.id,
        'item_id': item.id
    }
    return Response({'context': context}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def cart_details(request, pk=None):
    cart_obj = new_or_get(request, pk)
    serialized_cart = CartSerializer(cart_obj)
    return Response({'cart': serialized_cart.data})
    # return Response({'cart': serialized_cart.data})
    # items = cart_obj.items.all()
    # items = [item.product.id for item in items]
