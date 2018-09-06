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
        return self.category.label + ' | ' + self.label


class Build(models.Model):
    UNITS = (
        ('Square Foot', 'Square Foot'),
        ('Linear Foot', 'Linear Foot'),
        ('Cubic Foot', 'Cubic Foot'),
        ('Each', 'Each')
        )

    label = models.CharField(max_length=40)
    unit = models.CharField(max_length=50, choices=UNITS, default='not assigned')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="build_types",
        null=True
        )

    class Meta:
        unique_together = ('category', 'label')

    def __str__(self):
        return self.category.label + ' | ' + self.label

class Look(models.Model):
    label = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.label

class Finish(models.Model):
    label = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.label

class ShadeVariation(models.Model):
    label = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.label

class Product(models.Model):
    name = models.CharField(max_length=200)
    bb_sku = models.CharField(max_length=200, unique=True)

    manufacturer = models.ForeignKey(
        Manufacturer,
        null=True,
        related_name='products',
        on_delete=models.SET_NULL,
        )


    manufacturer_url = models.URLField(null=True, blank=True)
    lowest_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_priced = models.BooleanField(default=False)
    for_sale = models.BooleanField(default=False)
    image = models.ImageField(null=True)
    last_scraped = models.DateTimeField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    # categorized
    build = models.ForeignKey(Build, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, null=True, on_delete=models.SET_NULL)

    # application
    walls = models.BooleanField(default=False)
    countertops = models.BooleanField(default=False)
    floors = models.BooleanField(default=False)
    cabinet_fronts = models.BooleanField(default=False)

    # special area
    shower_floors = models.BooleanField(default=False)
    shower_walls = models.BooleanField(default=False)
    exterior = models.BooleanField(default=False)
    covered = models.BooleanField(default=False)
    pool_linings = models.BooleanField(default=False)

    thickness = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    manufacturer_sku = models.CharField(max_length=50, null=True, blank=True)
    manu_collection = models.CharField(max_length=50, null=True, blank=True)
    width = models.CharField(max_length=20, null=True, blank=True)
    length = models.CharField(max_length=20, null=True, blank=True)

    look = models.ForeignKey(Look, null=True, blank=True, on_delete=models.SET_NULL)
    image_2 = models.ImageField(null=True, blank=True)
    lrv = models.IntegerField(null=True, blank=True)
    cof = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    residential_warranty = models.IntegerField(null=True, blank=True)
    commercial_warranty = models.IntegerField(null=True, blank=True)
    finish = models.ForeignKey(Finish, null=True, on_delete=models.SET_NULL)
    shade_variation = models.ForeignKey(ShadeVariation, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(null=True, blank=True)

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
            values = sellers.values('price_per_unit', 'supplier', 'units_available', 'id')
            price = sellers.aggregate(Min('price_per_unit'))
            self.lowest_price = price["price_per_unit__min"]
            self.is_priced = True
            self.for_sale = True
            self.save()
            return values


    def manufacturer_name(self):
        return self.manufacturer.name

    def save(self, *args, **kwargs):
        if self.material:
            if self.material.category == self.build.category:
                super(Product, self).save(*args, **kwargs)
        else:
            super(Product, self).save(*args, **kwargs)

    def category_name(self):
        return self.build.category.label

    def category_id(self):
        return self.build.category.id

    def look_label(self):
        return self.look.label

    def size(self):
        return self.width + self.length
