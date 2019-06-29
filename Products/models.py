import uuid
from model_utils.managers import InheritanceManager
from django.contrib.postgres import fields as pg_fields
from django.contrib.gis.db import models
from django.db.models import Min, Avg
from django.contrib.gis.geos import MultiPoint


class Manufacturer(models.Model):
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class ProductAvailabilityQuerySet(models.QuerySet):
    def priced_in_store(self, location_pk=None):
        from Profiles.models import SupplierProduct
        if location_pk:
            pks = SupplierProduct.objects.filter(
                supplier__pk=location_pk,
                publish_in_store_price=True,
                ).values_list('product__pk', flat=True).distinct()
        else:
            pks = SupplierProduct.objects.filter(
                publish_in_store_price=True,).values_list('product__pk', flat=True).distinct()
        return self.filter(pk__in=pks)

    def available_in_store(self, location_pk=None):
        from Profiles.models import SupplierProduct
        if location_pk:
            pks = SupplierProduct.objects.filter(
                supplier__pk=location_pk,
                publish_in_store_availability=True,
                ).values_list('product__pk', flat=True).distinct()
        else:
            pks = SupplierProduct.objects.filter(
                publish_in_store_availability=True,).values_list('product__pk', flat=True).distinct()
        return self.filter(pk__in=pks)

    def safe_commands(self):
        return ('priced_in_store', 'available_in_store')




class Product(models.Model):
    SF = 'SF'
    EACH = 'EACH'
    UNIT_CHOICES = (
        (SF, 'SF'),
        (EACH, 'Each')
    )

    name = models.CharField(max_length=1200)
    bb_sku = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=SF)

    manufacturer_url = models.URLField(max_length=300, null=True, blank=True)
    manufacturer_sku = models.CharField(max_length=200, null=True, blank=True)
    manu_collection = models.CharField(max_length=200, null=True, blank=True)
    manufacturer_style = models.CharField(max_length=200, null=True, blank=True)

    swatch_image = models.ImageField()
    room_scene = models.ImageField()
    tiling_image = models.ImageField()

    lowest_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    average_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True)

    in_store = models.BooleanField(default=False)    
    online_and_priced = models.BooleanField(default=False)
    in_store_and_priced = models.BooleanField(default=False)
    installation_offered = models.BooleanField(default=False)
    locations = models.MultiPointField(null=True)

    residential_warranty = models.CharField(max_length=100, null=True, blank=True)
    commercial_warranty = models.CharField(max_length=100, null=True, blank=True)
    light_commercial_warranty = models.CharField(max_length=100, null=True)
    commercial = models.BooleanField(default=False)

    detail_response = pg_fields.JSONField(null=True, blank=True)

    manufacturer = models.ForeignKey(
        Manufacturer,
        null=True,
        related_name='products',
        on_delete=models.SET_NULL,
        )

    objects = InheritanceManager()
    availability = ProductAvailabilityQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_price(self, location_pk: int = None):
        if not location_pk:
            return self.lowest_price
        sup_prod = self.priced.filter(supplier=location_pk).first()
        if not sup_prod:
            return None
        return sup_prod.in_store_ppu

    def average_rating(self):
        avg_rating = self.ratings.all().aggregate(Avg('rating'))
        avg_rating = avg_rating.get('rating_avg', None)
        return avg_rating

    def rating_count(self):
        return self.ratings.all().count()

    def get_in_store(self):
        return self.priced.select_related(
            'supplier',
            'supplier__company_account',
            'supplier__address',
            'supplier__address__coordinates',
            'supplier__address__postal_code'
        ).filter(publish_in_store_availability=True)

    def get_online_priced(self):
        return self.priced.select_related(
            'supplier',
            'supplier__company_account',
            'supplier__address',
            'supplier__address__coordinates',
            'supplier__address__postal_code'
            ).filter(publish_online_price=True)

    def get_in_store_priced(self):
        return self.priced.select_related(
            'supplier',
            'supplier__company_account',
            'supplier__address',
            'supplier__address__coordinates',
            'supplier__address__postal_code'
        ).filter(publish_in_store_price=True)

    def set_prices(self):
        self.in_store = self.priced.all().filter(publish_in_store_availability=True).exist()
        self.in_store_and_priced = self.priced.all().filter(publish_in_store_price=True).exist()
        self.online_and_priced = self.priced.all().filter(publish_online_price=True).exist()
        if self.in_store_and_priced or self.online_and_priced:
            price = self.priced.all().aggregate(Min('in_store_ppu'), Avg('in_store_ppu'))
            self.lowest_price = price["in_store_ppu__min"]
            self.average_price = price['in_store_ppu__avg']
        self.save()

    def set_locations(self):
        self.locations = None
        in_store_sellers = self.priced.all().filter(publish_in_store_availability=True)
        if in_store_sellers.count() > 0:
            coordinates = [q.supplier.address.coordinates.point for q in in_store_sellers]
            points = MultiPoint(*coordinates)
            self.locations = points
            self.save()

    def manufacturer_name(self):
        if not self.manufacturer:
            return None
        return self.manufacturer.label

    def attribute_list(self):
        return [
            ['manufacturer', self.manufacturer_name()],
            ['manufacturer collection', self.manu_collection],
            ['manufacturer style', self.manufacturer_style],
            ['manufacturer sku', self.manufacturer_sku],
            ['residential_warranty', self.residential_warranty],
            ['commercial_warranty', self.commercial_warranty],
            ['light_commercial_warranty', self.light_commercial_warranty]
        ]


class ProductSubClass(Product):

    class Meta:
        abstract = True

    @classmethod
    def run_special(cls):
        if hasattr(cls, 'special_method'):
            special_method = getattr(cls, 'special_method')
            special_method()
