from django.db import models
from django.db.models import Min
from djmoney.models.fields import MoneyField
from Profiles.models import CompanyShippingLocation


class Manufacturer(models.Model):
    name            = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def products(self):
        try:
            products = self.products.all()
            return products
        except:
            return


class Application(models.Model):
    area            = models.CharField(max_length=100)

    def __str__(self):
        return self.area


class ProductType(models.Model):
    
    UNITS = (
        ('Square Foot', 'Square Foot'),
        ('Linear Foot', 'Linear Foot'),
        ('Cubic Foot', 'Cubic Foot'),
        ('Each', 'Each')
        )
    material        = models.CharField(max_length=100)
    unit            = models.CharField(max_length=50, choices=UNITS, default='not assigned')

    def __str__ (self):
        return self.material



class Product(models.Model):
    name            = models.CharField(max_length=200)
    manufacturer    = models.ForeignKey(
                                        Manufacturer,
                                        null=True,
                                        related_name='products',
                                        on_delete=models.SET_NULL,
                                        )
    image           = models.ImageField()
    application     = models.ManyToManyField(Application)
    product_type    = models.ForeignKey(
                                        ProductType, 
                                        null=True, 
                                        on_delete=models.SET_NULL
                                        )
    is_priced       = models.BooleanField(default=False)
    lowest_price    = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return self.name

    def units(self):
        try:
            return self.product_type.unit
        except:
            return


    def prices(self):
        try:
            suppliers = self.priced.filter(units_available__gt=0)
            values = suppliers.values('price_per_unit', 'supplier__email', 'units_available', 'id' )
            price = suppliers.aggregate(Min('price_per_unit'))
            self.lowest_price = price["price_per_unit__min"]
            self.is_priced = True
            return values
        except:
            return 

    def manufacturer_name(self):
        return self.manufacturer.name

    def material(self):
        return self.product_type.material


class SupplierProduct(models.Model):

    product             = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='priced')
    supplier            = models.ForeignKey(CompanyShippingLocation, on_delete=models.CASCADE, related_name='priced_products')
    price_per_unit      = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')
    units_available     = models.IntegerField(default=0)
    units_per_order     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    for_sale            = models.BooleanField(default=False)

    def name(self):
        return self.supplier.get_first_name()

    def __str__(self):
        return self.supplier.get_first_name() + ' ' + self.product.name

    class Meta:
        unique_together = ('product','supplier')

