from django.db import models
from django.db.models import Min


class Manufacturer(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def products(self):
        try:
            products = self.products
            return products
        except:
            return

class Category(models.Model):

    label = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.label

class Material(models.Model):

    label = models.CharField(max_length=40)
    category = models.ForeignKey(Category, related_name='materials', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('category', 'label')


    def __str__(self):
        return self.category.label + self.label


class Build(models.Model):
    UNITS = (
        ('Square Foot', 'Square Foot'),
        ('Linear Foot', 'Linear Foot'),
        ('Cubic Foot', 'Cubic Foot'),
        ('Each', 'Each')
        )

    label = models.CharField(max_length=40)
    unit = models.CharField(max_length=50, choices=UNITS, default='not assigned')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="build_types", null=True)

    class Meta:
        unique_together = ('category', 'label')

    def __str__(self):
        return self.category.label + self.label

class Look(models.Model):
    label = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.label


class Product(models.Model):
    name = models.CharField(max_length=200)

    manufacturer = models.ForeignKey(
                                        Manufacturer,
                                        null=True,
                                        related_name='products',
                                        on_delete=models.SET_NULL,
                                        )


    manufacturer_url = models.URLField(null=True, blank=True)
    lowest_price= models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_priced = models.BooleanField(default=False)
    for_sale = models.BooleanField(default=False)
    image = models.ImageField()
    
    # categorized
    build = models.ForeignKey(Build, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, null=True, on_delete=models.SET_NULL)

    # application
    walls = models.BooleanField(default=False)
    countertops = models.BooleanField(default=False)
    floors = models.BooleanField(default=False)

    # special area
    shower = models.BooleanField(default=False)
    exterior = models.BooleanField(default=False)
    covered = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)


    thickness = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    manufacturer_sku = models.CharField(max_length=50, null=True, blank=True)
    manu_collection = models.CharField(max_length=50, null=True, blank=True)

    look = models.ForeignKey(Look, null=True, on_delete=models.SET_NULL)
    image_2 = models.ImageField(null=True)
    lrv = models.IntegerField(null=True)
    cof = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    width = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    length = models.DecimalField(max_digits=6, decimal_places=3, null=True)


    def __str__(self):
        return self.name

    def units(self):
        try:
            return self.build.unit
        except:
            return


    def prices(self):
        sellers = self.priced.filter(for_sale=True)
        if sellers:
            values = sellers.values('price_per_unit', 'supplier', 'units_available', 'id' )
            price = sellers.aggregate(Min('price_per_unit'))
            self.lowest_price = price["price_per_unit__min"]
            self.is_priced = True
            self.for_sale = True
            self.save()
            return values
        else:
            return 


    def manufacturer_name(self):
        return self.manufacturer.name
