import decimal
from django.db import models
from django.conf import settings
from Profiles.models import SupplierProduct


# class CartManager(models.Manager):
#     def new_or_get(self, request):
#         cart_id = request.session.get("cart_id", None)
#         token = request
#         qs = super().get_queryset().filter(id=cart_id)
#         if qs.count() == 1:
#             new_obj = False
#             cart_obj = qs.first()

#             if request.user.is_authenticated and cart_obj.user is None:
#                 cart_obj.user = request.user
#                 cart_obj.save()
#         else:
#             cart_obj = Cart.objects.new(user=request.user)
#             new_obj = True
#             request.session['cart_id'] = cart_obj.id
#         return cart_obj, new_obj

#     def new(self, user=None):
#         user_obj = None
#         if user is not None:
#             if user.is_authenticated:
#                 user_obj = user
#         return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # objects = CartManager()

    def __str__(self):
        return str(self.id)

    def add_subtotal(self):
        total = decimal.Decimal('0.00')
        for item in self.items.all():
            total = total + item.total()
        return total

    def add_total(self):
        subtotal = self.add_subtotal()
        return subtotal * decimal.Decimal('1.08')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(SupplierProduct, on_delete=models.CASCADE, blank=True)
    quantity = models.IntegerField()

    def __str__(self):
        return str(self.id)

    def total(self):
        price = self.product.online_ppu
        quantity = str(self.quantity) + '.00'
        return price * decimal.Decimal(quantity)
