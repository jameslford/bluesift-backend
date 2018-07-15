from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField


class Manufacturer(models.Model):
    name            = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Application(models.Model):
    area            = models.CharField(max_length=100)

    def __str__(self):
        return self.area

    # def get_types(self):
    #     try:
    #         my_types = self.types.

class ProductType(models.Model):
    UNITS = (
        ('Square Foot', 'Square Foot'),
        ('Linear Foot', 'Linear Foot'),
        ('Cubic Foot', 'Cubic Foot'),
        ('Each', 'Each')
        )
    material        = models.CharField(max_length=100)
    unit            = models.CharField(max_length=50, choices=UNITS, default='not asssigned')

    # def get_application_names(self):
    #     try:
    #         applications = self.application.all().values_list('area', flat=True)
    #         return str(list(applications))
    #     except:
    #         return ''

    def __str__ (self):
        return self.material + str(self.pk) # +'  '+ self.get_application_names()

# class GetPriced(models.Manager):
#     def get_quer


class Product(models.Model):
    name            = models.CharField(max_length=200)
    manufacturer    = models.ForeignKey(
                        Manufacturer, 
                        on_delete=models.CASCADE,
                        )
    image           = models.ImageField()
    application     = models.ManyToManyField(Application)
    product_type    = models.ForeignKey(ProductType, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def is_priced(self):
        try:
            count = self.priced.count()
            if count > 0:
                return True
            return False
        except:
            return 

    def get_units(self):
        try:
            return self.product_type.unit
        except:
            return


    def get_suppliers(self):
        try:
            suppliers = self.priced.filter(units_available__gt=0).order_by('price_per_unit')
            values = suppliers.values('price_per_unit', 'supplier__email', 'units_available' ) 
            return values
        except:
            return 



class SupplierProduct(models.Model):

    product             = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='priced')
    supplier            = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                            on_delete=models.CASCADE, 
                                            related_name='supplier_products',
                                            limit_choices_to={'is_supplier' : True}
                                            )
    price_per_unit      = MoneyField(max_digits=8, decimal_places=2, default_currency='USD')
    units_available     = models.IntegerField(default=0)
    units_per_order     = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def name(self):
        return self.supplier.get_first_name()

    def __str__(self):
        return self.supplier.get_first_name() + ' ' + self.product.name

    class Meta:
        unique_together = ('product','supplier')

