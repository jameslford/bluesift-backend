"""
Main product class, very other type of product(specialized, project & retailer) is derived from Product class below
"""

import uuid
from django.contrib.postgres import fields as pg_fields
from django.contrib.gis.db import models
from django.forms.models import model_to_dict
from django.db.models import (
    Subquery,
    OuterRef,
    CharField
)
from django.db.models.functions import Least
from django.contrib.gis.geos import MultiPoint
from model_utils.managers import InheritanceManager
from Addresses.models import Coordinate


def availability_getter(query_term, location_pk=None):
    from Suppliers.models import SupplierProduct
    term = {query_term: True}
    if location_pk:
        term['retailer_id'] = location_pk
    return SupplierProduct.objects.filter(**term).values_list('product__pk', flat=True).distinct()


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
        from Suppliers.models import SupplierProduct
        if location_pk:
            sup_prods = SupplierProduct.objects.filter(
                retailer__id=location_pk).filter(product__in=Subquery(self.values('pk')))
        else:
            sup_prods = SupplierProduct.objects.filter(product__in=Subquery(self.values('pk')))
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
        from Suppliers.models import SupplierProduct
        term = {'product__pk': OuterRef('pk'), 'publish_in_store_price': True}
        if location_pk:
            term['retailer__pk'] = location_pk
        sup_prods = (
            SupplierProduct
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


class ProductPricingManager(models.Manager):
    def get_queryset(self):
        """ just points to qset """
        return ProductAvailabilityQuerySet(self.model, using=self._db)

    def filter_availability(self, command, location_pk=None, pk_only=False):
        """ just points to qset """
        return self.get_queryset().filter_availability(command, location_pk, pk_only)

    def priced_in_store(self, location_pk=None):
        """ just points to qset """
        return self.get_queryset().priced_in_store(location_pk)

    def available_in_store(self, location_pk=None):
        """ just points to qset """
        return self.get_queryset().available_in_store(location_pk)

    def retailer_products(self, location_pk=None):
        """ just points to qset """
        return self.get_queryset().retailer_products(location_pk)

    def safe_availability_commands(self):
        """ just points to qset """
        return self.get_queryset().safe_availability_commands()

    def product_prices(self, location_pk=None):
        """ just points to qset """
        return self.get_queryset().product_prices(location_pk)


def get_3d_return_path(instance, filename=None):
    return f'geometry/{instance.bb_sku}/{filename}'


class Product(models.Model):
    SF = 'SF'
    EACH = 'EACH'
    UNIT_CHOICES = (
        (SF, 'SF'),
        (EACH, 'Each')
    )

    name = models.CharField(max_length=1200, blank=True)
    bb_sku = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=SF, blank=True)

    manufacturer_url = models.URLField(max_length=300, null=True, blank=True)
    manufacturer_sku = models.CharField(max_length=200, null=True, blank=True)
    manufacturer_collection = models.CharField(max_length=200, null=True, blank=True)
    manufacturer_style = models.CharField(max_length=200, null=True, blank=True)

    swatch_image = models.ImageField(upload_to='swatches/')
    room_scene = models.ImageField(upload_to='rooms/', null=True, blank=True)
    tiling_image = models.ImageField(upload_to='tiles/', null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True)

    in_store = models.BooleanField(default=False)
    online_and_priced = models.BooleanField(default=False)
    in_store_and_priced = models.BooleanField(default=False)
    installation_offered = models.BooleanField(default=False)
    locations = models.MultiPointField(null=True, blank=True)

    residential_warranty = models.CharField(max_length=100, null=True, blank=True)
    commercial_warranty = models.CharField(max_length=100, null=True, blank=True)
    light_commercial_warranty = models.CharField(max_length=100, null=True, blank=True)
    commercial = models.BooleanField(default=False)

    _dxf_file = models.FileField(null=True, blank=True, upload_to=get_3d_return_path)
    _rfa_file = models.FileField(null=True, blank=True, upload_to=get_3d_return_path)
    _ipt_file = models.FileField(null=True, blank=True, upload_to=get_3d_return_path)
    _dwg_3d_file = models.FileField(null=True, blank=True, upload_to=get_3d_return_path)
    _dwg_2d_file = models.FileField(null=True, blank=True, upload_to=get_3d_return_path)
    _obj_file = models.FileField(null=True, blank=True, upload_to=get_3d_return_path)
    _mtl_file = models.FileField(null=True, blank=True, upload_to=get_3d_return_path)

    dxf_file = models.URLField(null=True, blank=True, max_length=1000)
    rfa_file = models.URLField(null=True, blank=True, max_length=1000)
    ipt_file = models.URLField(null=True, blank=True, max_length=1000)
    dwg_3d_file = models.URLField(null=True, blank=True, max_length=1000)
    dwg_2d_file = models.URLField(null=True, blank=True, max_length=1000)
    obj_file = models.URLField(null=True, blank=True, max_length=1000)
    mtl_file = models.URLField(null=True, blank=True, max_length=1000)

    derived_gbl = models.FileField(null=True, blank=True, upload_to=get_3d_return_path)
    derived_width = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    derived_height = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    derived_depth = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    derived_center = pg_fields.ArrayField(models.FloatField(null=True, blank=True), null=True, blank=True, size=3)

    geometry_clean = models.BooleanField(default=False)
    detail_response = pg_fields.JSONField(null=True, blank=True)

    manufacturer = models.ForeignKey(
        Manufacturer,
        null=True,
        related_name='products',
        on_delete=models.SET_NULL,
        )

    objects = ProductPricingManager()
    subclasses = InheritanceManager()

    class Meta:
        unique_together = ('manufacturer', 'manufacturer_sku')

    def __str__(self):
        return f'{self.manufacturer.label}, {self.manufacturer_collection}, {self.manufacturer_style}'

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = str(self.bb_sku)
        super(Product, self).save(*args, **kwargs)

    def get_in_store(self):
        return self.priced.select_related(
            'location',
            'location__company',
            'location__address',
            'location__address__coordinates',
            'location__address__postal_code'
        ).filter(publish_in_store_availability=True)

    def get_online_priced(self):
        return self.priced.select_related(
            'location',
            'location__company',
            'location__address',
            'location__address__coordinates',
            'location__address__postal_code'
            ).all().filter(publish_online_price=True)

    def get_in_store_priced(self):
        return self.priced.select_related(
            'location',
            'location__company',
            'location__address',
            'location__address__coordinates',
            'location__address__postal_code'
        ).all().filter(publish_in_store_price=True)

    def set_locations(self):
        self.locations = None
        in_store_sellers = self.priced.all().filter(publish_in_store_availability=True)
        if in_store_sellers.count() > 0:
            coordinates = [q.location.address.coordinates.point for q in in_store_sellers]
            points = MultiPoint(*coordinates)
            self.locations = points
            self.save()

    def set_location_from_retailer(self, coordinates: Coordinate):
        points = MultiPoint(coordinates.point)
        self.locations = points
        self.save()

    def set_name(self):
        sub = Product.subclasses.get_subclass(pk=self.pk)
        fields = [
            'manufacturer',
            'manufacturer_style',
            'manufacturer_collection',
            'manufacturer_sku'
            ] + sub.name_fields
        vals = list(model_to_dict(sub, fields=fields).values())
        vals = [str(val) for val in vals]
        self.name = '*$'.join(vals)
