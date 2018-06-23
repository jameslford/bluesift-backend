# Libraries.models.py

from django.db import models
from django.conf import settings
from Products.models import Product
from djmoney.models.fields import MoneyField


class SupplierProduct(models.Model):
    UNITS = (
        (0,'Square Foot'),
        (1, 'Linear Foot'),
        (2, 'Cubic Foot'),
        (3, 'Each')
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price_per_unit = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')
    unit = models.SmallIntegerField(choices=UNITS)

    class Meta:
        unique_together = ('product','supplier')



class Library(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    materials = models.ManyToManyField(Product)
   



