from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from Profiles.models import SupplierProduct
from .models import Cart, CartItem
from .serializers import CartSerializer


@api_view(['POST'])
def add_to_cart(request):
    supplier_product_id = request.POST.get('supplier_product_id', None)
    supplier_product_id = int(supplier_product_id)
    cart_id = request.POST.get('cart_id', None)
    qty = request.POST.get('qty')
    qty = int(qty)
    if supplier_product_id is not None:
        try:
            prod_obj = SupplierProduct.objects.get(id=supplier_product_id)
        except SupplierProduct.DoesNotExist:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)
    qs = Cart.objects.filter(id=cart_id)
    if qs.count() == 1:
        cart_obj = qs.first()

        if request.user.is_authenticated and cart_obj.user is None:
            cart_obj.user = request.user
            cart_obj.save()
    else:
        cart_obj = Cart.objects.create(user=request.user)
    for item in cart_obj.items.all():
        if item.product == prod_obj:
            qty = qty + item.quantity
            item.delete()
    if prod_obj.units_available < qty:
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
def cart_details(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    serialized_cart = CartSerializer(cart_obj)
    # return Response({'cart': serialized_cart.data})
    # items = cart_obj.items.all()
    # items = [item.product.id for item in items]
    return Response({
        'cart': serialized_cart.data,
        })
