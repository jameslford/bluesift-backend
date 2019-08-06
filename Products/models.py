import uuid
from model_utils.managers import InheritanceManager
from django.contrib.postgres import fields as pg_fields
from django.contrib.gis.db import models
from django.db.models import (
    Avg,
    Subquery,
    OuterRef,
    CharField
    # Min,
    # Count,
    # FloatField,
)
from django.db.models.functions import Least
from django.contrib.gis.geos import MultiPoint


def availability_getter(query_term, location_pk=None):
    from UserProducts.models import RetailerProduct
    term = {query_term: True}
    if location_pk:
        term['retailer_id'] = location_pk
    return RetailerProduct.objects.filter(**term).values_list('product__pk', flat=True).distinct()


class Manufacturer(models.Model):
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class ProductAvailabilityQuerySet(models.QuerySet):
    def priced_in_store(self, location_pk=None, pk_only=False):
        pks = availability_getter('publish_in_store_price', location_pk)
        if pk_only:
            return pks
        return self.filter(pk__in=Subquery(pks))

    def available_in_store(self, location_pk=None, pk_only=False):
        pks = availability_getter('publish_in_store_availability', location_pk)
        if pk_only:
            return pks
        return self.filter(pk__in=Subquery(pks))

    def priced_online(self, location_pk=None, pk_only=False):
        pks = availability_getter('publish_online_price', location_pk)
        if pk_only:
            return pks
        return self.filter(pk__in=Subquery(pks))

    def installation_offered(self, location_pk=None, pk_only=False):
        pks = availability_getter('offer_installation', location_pk)
        if pk_only:
            return pks
        return self.filter(pk__in=Subquery(pks))

    def retailer_products(self, location_pk=None):
        from UserProducts.models import RetailerProduct
        if location_pk:
            sup_prods = RetailerProduct.objects.filter(retailer__id=location_pk).filter(product__in=Subquery(self.values('pk')))
        else:
            sup_prods = RetailerProduct.objects.filter(product__in=Subquery(self.values('pk')))
        return sup_prods

    def filter_availability(self, commands, location_pk=None, pk_only=False):
        pk_sets = []
        clist = commands if isinstance(commands, list) else [commands]
        for command in clist:
            if command not in self.safe_availability_commands():
                pk_sets = []
                raise Exception(f'Unsafe method - {command}')
            func = getattr(self, command, None)
            if not func:
                pk_sets = []
                raise Exception(f'Unsafe method - {command}')
            if not pk_only:
                return func(location_pk)
            pk_sets.append(func(location_pk, pk_only))
        q_object = models.Q()
        for pks in pk_sets:
            term = {'pk__in': pks}
            q_object |= models.Q(**term)
        return self.filter(q_object)

    def safe_availability_commands(self):
        return ('available_in_store', 'priced_in_store', 'installation_offered')

    def product_prices(self, location_pk=None):
        from UserProducts.models import RetailerProduct
        term = {'product__pk': OuterRef('pk')}
        if location_pk:
            term['retailer__pk'] = location_pk
        sup_prods = (
            RetailerProduct
            .objects
            .filter(**term).only('in_store_ppu', 'online_ppu')
            .annotate(min_price=Least('in_store_ppu', 'online_ppu'))
            .order_by('min_price')
            .values('min_price')[:1]
        )

        return self.annotate(
            low_price=Subquery(
                sup_prods,
                output_field=CharField()
            )
        )

    def get_lowest(self, location_pk=None):
        from UserProducts.models import RetailerProduct
        term = {'product__in': self.values('pk')}
        if location_pk:
            term['retailer__pk'] = location_pk
        sup_prods = RetailerProduct.objects.filter(**term).only('in_store_ppu', 'online_ppu').annotate(
            min_price=Least('in_store_ppu', 'online_ppu')
        )
        return list(sup_prods.values('min_price', 'product__pk'))


class ProductPricingManager(models.Manager):
    def get_queryset(self):
        return ProductAvailabilityQuerySet(self.model, using=self._db)

    def filter_availability(self, command, location_pk=None, pk_only=False):
        return self.get_queryset().filter_availability(command, location_pk, pk_only)

    def priced_in_store(self, location_pk=None):
        return self.get_queryset().priced_in_store(location_pk)

    def available_in_store(self, location_pk=None):
        return self.get_queryset().available_in_store(location_pk)

    def retailer_products(self, location_pk=None):
        return self.get_queryset().retailer_products(location_pk)

    def safe_availability_commands(self):
        return self.get_queryset().safe_availability_commands()

    def product_prices(self, location_pk=None):
        return self.get_queryset().product_prices(location_pk)


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

    objects = ProductPricingManager()
    subclasses = InheritanceManager()

    def __str__(self):
        return self.name

    def average_rating(self):
        avg_rating = self.ratings.all().aggregate(Avg('rating'))
        avg_rating = avg_rating.get('rating_avg', None)
        return avg_rating

    def rating_count(self):
        return self.ratings.all().count()

    def get_in_store(self):
        return self.priced.select_related(
            'retailer',
            'retailer__company',
            'retailer__address',
            'retailer__address__coordinates',
            'retailer__address__postal_code'
        ).filter(publish_in_store_availability=True)

    def get_online_priced(self):
        return self.priced.select_related(
            'retailer',
            'retailer__company',
            'retailer__address',
            'retailer__address__coordinates',
            'retailer__address__postal_code'
            ).filter(publish_online_price=True)

    def get_in_store_priced(self):
        return self.priced.select_related(
            'retailer',
            'retailer__company',
            'retailer__address',
            'retailer__address__coordinates',
            'retailer__address__postal_code'
        ).filter(publish_in_store_price=True)

    def set_locations(self):
        self.locations = None
        in_store_sellers = self.priced.all().filter(publish_in_store_availability=True)
        if in_store_sellers.count() > 0:
            coordinates = [q.retailer.address.coordinates.point for q in in_store_sellers]
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

    @classmethod
    def validate_sub(cls, sub: str):
        return bool(sub.lower() in [klas.__name__.lower() for klas in cls.__subclasses__()])

    @classmethod
    def return_sub(cls, sub: str):
        classes = [klas for klas in cls.__subclasses__() if klas.__name__.lower() == sub.lower()]
        if classes:
            return classes[0]
        return None
