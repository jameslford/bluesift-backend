"""
Main product class, very other type of product(specialized, project & retailer) is derived from Product class below
"""

import uuid
from django.contrib.postgres import fields as pg_fields
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.postgres.fields import JSONField
from django.contrib.gis.geos import MultiPoint
from django.contrib.contenttypes.models import ContentType

# from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.db.models import Min, Case, When
from django.db.models.functions import Least
from django.db import transaction
from model_utils.managers import InheritanceManager
from Addresses.models import Coordinate, Zipcode


class Manufacturer(models.Model):
    label = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.label


class InitialProductValues(models.Model):
    product = models.ForeignKey("Products.Product", on_delete=models.CASCADE)
    values = JSONField()


class ValueCleanerManager(models.Manager):
    def create_and_apply_async(self, product_class: str, field, new_value, old_value):
        from .tasks import add_value_cleaner

        add_value_cleaner.delay(product_class, field, new_value, old_value)


class ValueCleaner(models.Model):
    product = models.ForeignKey("Products.Product", on_delete=models.CASCADE)
    field = models.CharField(max_length=60)
    initial_value = models.CharField(max_length=200, default="")
    new_value = models.CharField(max_length=200)
    objects = ValueCleanerManager()

    class Meta:
        unique_together = ["product", "field"]

    @classmethod
    @transaction.atomic
    def create_or_update(cls, product_class, field, new_value, old_value):
        if isinstance(product_class, str):
            from config.globals import check_department_string

            product_class = check_department_string(product_class)
        lookup_arg = {field: old_value}
        products = product_class.objects.filter(**lookup_arg)
        for product in products:
            vac, created = cls.objects.get_or_create(product=product, field=field)
            if created:
                vac.initial_value = old_value
                vac.new_value = new_value
                vac.save()
                setattr(product, field, new_value)
                product.save()
                return
            if not vac.initial_value:
                vac.initial_value = getattr(product, field)
            vac.new_value = new_value
            vac.save()
            setattr(product, field, new_value)
            product.save()
            return


class ProductAvailabilityQuerySet(models.QuerySet):
    def product_prices(self):
        prods = self.annotate(
            low_price=Case(
                When(
                    priced__publish_in_store_price=True,
                    then=Least(Min("priced__in_store_ppu"), Min("priced__online_ppu")),
                )
            )
        )
        return prods


class ProductPricingManager(models.Manager):
    def get_queryset(self):
        """ just points to qset """
        return ProductAvailabilityQuerySet(self.model, using=self._db)

    def product_prices(self):
        """ just points to qset """
        return self.get_queryset().product_prices()


def get_3d_return_path(instance, filename=None):
    return f"geometry/{instance.bb_sku}/{filename}"


class Product(models.Model):
    SF = "SF"
    EACH = "EACH"
    UNIT_CHOICES = ((SF, "SF"), (EACH, "Each"))

    name = models.CharField(max_length=1200, blank=True)
    bb_sku = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    hash_value = models.CharField(max_length=1200, blank=True, null=True, unique=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=SF, blank=True)
    category = models.CharField(max_length=80, blank=True, null=True)

    manufacturer_url = models.URLField(max_length=300, null=True, blank=True)
    manufacturer_sku = models.CharField(max_length=200)
    manufacturer_collection = models.CharField(max_length=200, null=True, blank=True)
    manufacturer_style = models.CharField(max_length=200, null=True, blank=True)

    swatch_image_original = models.URLField(max_length=1000)
    room_scene_original = models.URLField(max_length=1000, null=True, blank=True)
    tiling_image_original = models.URLField(max_length=1000, null=True, blank=True)

    swatch_image = models.ImageField(upload_to="swatches/")
    room_scene = models.ImageField(upload_to="rooms/", null=True, blank=True)
    tiling_image = models.ImageField(upload_to="tiles/", null=True, blank=True)

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
    derived_width = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True
    )
    derived_height = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True
    )
    derived_depth = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True
    )
    derived_center = pg_fields.ArrayField(
        models.FloatField(null=True, blank=True), null=True, blank=True, size=3
    )

    geometry_clean = models.BooleanField(default=False)
    detail_response = pg_fields.JSONField(null=True, blank=True)

    manufacturer = models.ForeignKey(
        Manufacturer, null=True, related_name="products", on_delete=models.SET_NULL,
    )

    objects = ProductPricingManager()
    subclasses = InheritanceManager()

    name_fields = []

    class Meta:
        unique_together = ("manufacturer", "manufacturer_sku")

    def __str__(self):
        return f"{self.manufacturer_collection}, {self.manufacturer_style}"

    def __static_tags(self):
        return []

    def __dynamic_tags(self):
        return [
            self.manufacturer.label,
            self.manufacturer_collection,
            self.manufacturer_style,
            self.manufacturer_sku,
        ]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.category = self.__class__.__name__
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def tags(self):
        return self.__static_tags() + self.__dynamic_tags()

    def assign_name(self):
        raise Exception("must be set on subclass")

    def get_name(self):
        return self.assign_name()

    def get_in_store(self):
        return self.priced.select_related(
            "location",
            "location__company",
            "location__address",
            "location__address__coordinates",
            "location__address__postal_code",
        ).filter(publish_in_store_availability=True)

    def get_online_priced(self):
        return (
            self.priced.select_related(
                "location",
                "location__company",
                "location__address",
                "location__address__coordinates",
                "location__address__postal_code",
            )
            .all()
            .filter(publish_online_price=True)
        )

    def get_in_store_priced(self, zipcode=None):
        priced = (
            self.priced.select_related(
                "location",
                "location__company",
                "location__address",
                "location__address__coordinates",
                "location__address__postal_code",
            )
            .all()
            .filter(publish_in_store_price=True)
        )
        if zipcode:
            point = Zipcode.objects.get(code=zipcode).centroid.point
            return priced.annotate(
                distance=Distance("location__address__coordinates__point", point)
            )
        return priced

    def serialize_priced(self, zipcode=None):
        priced = self.get_in_store_priced(zipcode)
        return [
            {
                "pk": price.pk,
                "in_store_ppu": price.in_store_ppu,
                "units_available_in_store": price.units_available_in_store,
                "units_per_order": price.units_per_order,
                "location_address": price.location.address.city_state(),
                "location_id": price.location.pk,
                "company_name": price.location.company.name,
                "lead_time_ts": price.lead_time_ts.days,
                "publish_online_price": price.publish_online_price,
                "publish_in_store_price": price.publish_in_store_price,
                "publish_in_store_availability": price.publish_in_store_availability,
                "distance": str(int(round(float(price.distance.mi), 0)))
                if zipcode
                else "Use Location",
            }
            for price in priced
        ]

    def set_locations(self):
        self.locations = None
        in_store_sellers = self.priced.all().filter(publish_in_store_availability=True)
        if in_store_sellers.count() > 0:
            coordinates = [
                q.location.address.coordinates.point for q in in_store_sellers
            ]
            points = MultiPoint(*coordinates)
            self.locations = points
            self.save()

    def set_location_from_retailer(self, coordinates: Coordinate):
        points = MultiPoint(coordinates.point)
        self.locations = points
        self.save()

    def get_hash_value(self):
        fields = [
            "manufacturer",
            "manufacturer_style",
            "manufacturer_collection",
            "manufacturer_sku",
        ] + self.name_fields
        vals = list(model_to_dict(self, fields=fields).values())
        vals = [str(val) for val in vals]
        return " ".join(vals)

    def scraper_save(self):
        if not self.manufacturer_sku:
            return None
        alt_prod = Product.subclasses.filter(
            manufacturer=self.manufacturer, manufacturer_sku=self.manufacturer_sku
        ).select_subclasses()
        if not alt_prod:
            self.save()
            return self
        if alt_prod.count() > 1:
            return alt_prod.first()
        alt_prod = alt_prod.first()
        original_values = alt_prod.__dict__
        new_values = self.__dict__
        for field, value in original_values.items():
            if field in ["bb_sku", "_state"]:
                continue
            new_val = new_values.get(field)
            if value:
                if not new_val:
                    continue
            if new_val:
                setattr(alt_prod, field, new_val)
        alt_prod.save()
        return alt_prod

    @classmethod
    def create_facets(cls):
        from ProductFilter.models import BaseFacet

        cproduct = ContentType.objects.get_for_model(Product)
        BaseFacet.objects.get_or_create(
            content_type=cproduct,
            attribute="locations",
            widget="location",
            dynamic=True,
            field_type="MultiPointField",
            name="location",
        )
        BaseFacet.objects.get_or_create(
            content_type=cproduct,
            attribute="manufacturer",
            field_type="ForeignKey",
            widget="checkbox",
            name="manufacturers",
        )
        BaseFacet.objects.get_or_create(
            content_type=cproduct,
            name="file_types",
            field_type="FileField",
            attribute_list=[
                "_dxf_file",
                "_rfa_file",
                "_ipt_file",
                "_dwg_3d_file",
                "_dwg_2d_file",
            ],
        )
