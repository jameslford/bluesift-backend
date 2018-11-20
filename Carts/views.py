from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from Profiles.models import SupplierProduct
from .models import Cart, CartItem
from .serializers import CartSerializer


@api_view(['POST'])
def add_to_cart(request):
    supplier_product_id = request.POST.get('supplier_product_id', None)
    cart_id = request.POST.get('cart_id', None)
    qty = request.POST.get('qty')
    qty = int(qty)

    if supplier_product_id:
        supplier_product_id = int(supplier_product_id)
        try:
            prod_obj = SupplierProduct.objects.get(id=supplier_product_id)
        except SupplierProduct.DoesNotExist:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)

    if cart_id:
        cart_id = int(cart_id)
        cart_obj = Cart.objects.get_or_create(id=cart_id)[0]
    else:
        cart_obj = Cart.objects.create()

    if request.user.is_authenticated and cart_obj.user is None:
        cart_obj.user = request.user
        cart_obj.save()

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
def cart_details(request, pk):
    # cart_id = request.GET.get('cart_id', None)
    cart_obj = Cart.objects.get_or_create(id=pk)[0]
    if request.user.is_authenticated and cart_obj.user is None:
        cart_obj.user = request.user
        cart_obj.save()
    serialized_cart = CartSerializer(cart_obj)
    # return Response({'cart': serialized_cart.data})
    # items = cart_obj.items.all()
    # items = [item.product.id for item in items]
    return Response({
        'cart': serialized_cart.data,
        })
