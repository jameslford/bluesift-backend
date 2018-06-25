from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField


class Manufacturer(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class Product(models.Model):
    name            = models.CharField(max_length=200)
    manufacturer    = models.ForeignKey(
                        Manufacturer, 
                        on_delete=models.CASCADE,
                        )
    image           = models.ImageField()

    def __str__(self):
        return self.name

    def is_priced(self):
        if self.priced:
            return True
        return False

    def get_suppliers(self):
        if self.priced:
            suppliers = self.priced.all()
            return suppliers



class SupplierProduct(models.Model):
    UNITS = (
        (0,'Square Foot'),
        (1, 'Linear Foot'),
        (2, 'Cubic Foot'),
        (3, 'Each')
    )

    product             = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='priced')
    supplier            = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                            on_delete=models.CASCADE, 
                                            related_name='supplier_products',
                                            limit_choices_to={'is_supplier' : True}
                                            )
    price_per_unit      = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')
    unit                = models.SmallIntegerField(choices=UNITS)

    def __str__(self):
        return self.supplier.get_first_name() + ' ' + self.product.name

    class Meta:
        unique_together = ('product','supplier')

