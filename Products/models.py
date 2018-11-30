from django.db import models
from django.contrib.gis.db import models as g_models
from django.db.models import Min
from Addresses.models import Coordinate


class Manufacturer(models.Model):
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label

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
    # UNITS = (
    #     ('Square Foot', 'Square Foot'),
    #     ('Linear Foot', 'Linear Foot'),
    #     ('Cubic Foot', 'Cubic Foot'),
    #     ('Each', 'Each')
    #     )
    # unit = models.CharField(max_length=50, choices=UNITS, default='not assigned')

    label = models.CharField(max_length=40)
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

class Image(models.Model):
    original_url = models.CharField(max_length=300, unique=True)
    image = models.ImageField(max_length=300, null=True)

    def __str__(self):
        return self.original_url

class Product(models.Model):
    name = models.CharField(max_length=300)
    bb_sku = models.CharField(max_length=300, unique=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        null=True,
        related_name='products',
        on_delete=models.SET_NULL,
        )

    manufacturer_url = models.URLField(null=True, blank=True)
    image = models.ForeignKey(Image, null=True, on_delete=models.SET_NULL)
    last_scraped = models.DateTimeField(null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True)

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
    manu_collection = models.CharField(max_length=200, null=True, blank=True)
    manufacturer_color = models.CharField(max_length=200, null=True, blank=True)
    width = models.CharField(max_length=20, null=True, blank=True)
    length = models.CharField(max_length=20, null=True, blank=True)

    look = models.ForeignKey(Look, null=True, blank=True, on_delete=models.SET_NULL)
    image_2 = models.ImageField(null=True, blank=True)
    lrv = models.IntegerField(null=True, blank=True)
    cof = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    residential_warranty = models.IntegerField(null=True, blank=True)
    commercial_warranty = models.IntegerField(null=True, blank=True)
    finish = models.ForeignKey(Finish, null=True, blank=True, on_delete=models.SET_NULL)
    shade_variation = models.ForeignKey(ShadeVariation, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(null=True, blank=True)
    lowest_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    for_sale_online = models.BooleanField(default=False)
    for_sale_in_store = models.BooleanField(default=False)
    locations = g_models.MultiPointField(null=True)

    # location

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.material:
            if self.material.category == self.build.category:
                super(Product, self).save(*args, **kwargs)
        super(Product, self).save(*args, **kwargs)

    # def units(self):
    #     try:
    #         return self.build.unit
    #     except:
    #         return

    # def in_store_sellers(self):
    #     in_store_sellers = self.priced.filter(for_sale_in_store=True)
    #     if in_store_sellers:
    #         return in_store_sellers

    # def online_sellers(self):
    #     online_sellers = self.priced.filter(for_sale_online=True)
    #     if online_sellers:
    #         return online_sellers
        

    def set_prices(self):
        self.for_sale_in_store = False
        self.for_sale_online = False
        self.lowest_price = None
        online_sellers = self.priced.filter(for_sale_online=True)
        if online_sellers.count() > 0:
            self.for_sale_online = True
            self.save()
            return
        in_store_sellers = self.priced.filter(for_sale_in_store=True)
        if in_store_sellers.count() > 0:
            self.for_sale_in_store = True
            self.save()
            return
        all_sellers = online_sellers | in_store_sellers
        all_sellers = all_sellers.distinct()
        if all_sellers.count() > 0:
            price = all_sellers.aggregate(Min('my_price'))
            self.lowest_price = price["my_price__min"]
            self.save()
            return
        self.save()
        return

    def set_locations(self):
        self.locations = None
        in_store_sellers = self.priced.filter(for_sale_in_store=True)
        if in_store_sellers.count() > 0:
            coordinates = [q.supplier.address.coordinates.get_point() for q in in_store_sellers]
            points = tuple(coordinates)
            self.locations = points
            self.save()


    # def set_location(self):
    #         for loc in coordinates:
    #             self.locations.add(loc)







    # def prices(self):
    #     sellers  = self.priced.filter(for_sale_online=True)
    #     sellers = sellers | self.priced.filter(for_sale_in_store=True)
    #     if sellers.count() > 0:
    #         values = sellers.values(
    #             'online_ppu',
    #             'my_price',
    #             'for_sale_online',
    #             'for_sale_in_store',
    #             'supplier',
    #             'units_available',
    #             'units_per_order',
    #             'id',
    #             'supplier__address__address_line_1',
    #             'supplier__address__address_line_2',
    #             'supplier__address__city',
    #             'supplier__address__state',
    #             'supplier__address__postal_code',
    #             'supplier__company_account__name'
    #             )
    #         return values



    def manufacturer_name(self):
        return self.manufacturer.label



    def category_name(self):
        return self.build.category.label

    def category_id(self):
        return self.build.category.id

    def look_label(self):
        if self.look:
            return self.look.label
        else:
            return None

    def build_label(self):
        if self.build:
            return self.build.label
        else:
            return None

    def material_label(self):
        if self.material:
            return self.material.label
        else:
            return None
    
    def finish_label(self):
        if self.finish:
            return self.finish.label

    def size(self):
        return self.width + self.length

    def actual_image(self):
        return self.image.image
