import uuid
from dataclasses import dataclass, asdict
from dataclasses import field as dfield
from typing import List
from model_utils.managers import InheritanceManager
from django.contrib.postgres import fields as pg_fields
from django.contrib.gis.db import models
from django.db.models import Min, Avg
from django.contrib.gis.geos import MultiPoint
from ProductFilter.models import Sorter, ProductFilter
from Profiles.serializers import SupplierProductMiniSerializer


class Manufacturer(models.Model):
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label

    def products(self):
        try:
            products = self.products
            return products
        except:
            return None


class Product(models.Model):
    SF = 'SF'
    EACH = 'EACH'
    UNIT_CHOICES = (
        (SF, 'SF'),
        (EACH, 'Each')
    )

    name = models.CharField(max_length=1200)
    bb_sku = models.UUIDField(primary_key=True, unique=True, editable=False)
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

    for_sale_online = models.BooleanField(default=False)
    for_sale_in_store = models.BooleanField(default=False)
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


    def __str__(self):
        return self.name

    def average_rating(self):
        avg_rating = self.ratings.all().aggregate(Avg('rating'))
        avg_rating = avg_rating.get('rating_avg', None)
        return avg_rating

    def rating_count(self):
        return self.ratings.all().count()

    def online_priced(self):
        return self.priced.select_related(
            'supplier',
            'supplier__company_account',
            'supplier__address',
            'supplier__address__coordinates',
            'supplier__address__postal_code'
            ).filter(for_sale_online=True)

    def in_store_priced(self):
        return self.priced.select_related(
            'supplier',
            'supplier__company_account',
            'supplier__address',
            'supplier__address__coordinates',
            'supplier__address__postal_code'
        ).filter(for_sale_in_store=True)

    def set_prices(self):
        self.for_sale_in_store = False
        self.for_sale_online = False
        self.lowest_price = None
        online_sellers = self.priced.filter(for_sale_online=True)
        if online_sellers.count() > 0:
            self.for_sale_online = True
        in_store_sellers = self.priced.filter(for_sale_in_store=True)
        if in_store_sellers.count() > 0:
            self.for_sale_in_store = True
        all_sellers = online_sellers | in_store_sellers
        all_sellers = all_sellers.distinct()
        if all_sellers.count() > 0:
            price = all_sellers.aggregate(Min('in_store_ppu'), Avg('in_store_ppu'))
            self.lowest_price = price["in_store_ppu__min"]
            self.average_price = price['in_store_ppu__avg']
        self.save()
        return

    def set_locations(self):
        self.locations = None
        in_store_sellers = self.priced.filter(for_sale_in_store=True)
        if in_store_sellers.count() > 0:
            coordinates = [q.supplier.address.coordinates.point for q in in_store_sellers]
            points = MultiPoint(*coordinates)
            self.locations = points
            self.save()

    def set_response(self, pk):
        detail_builder = DetailBuilder(pk)
        return detail_builder

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


@dataclass
class DetailListItem:
    name: str = None
    terms: List = dfield(default_factory=lambda: [])

@dataclass
class DetailResponse:
    unit: str = None
    manufacturer: str = None
    manufacturer_url: str = None
    swatch_image: str = None
    room_scene: str = None
    priced: List = dfield(default_factory=lambda: [])
    lists: List[DetailListItem] = dfield(default_factory=lambda: [])


class DetailBuilder:

    def __init__(self, pk: str):
        self.bb_sku = pk
        self.product = self.get_subclass_instance()
        self.response: DetailResponse = DetailResponse()

    def get_subclass_instance(self):
        product = Product.obejcts.filter(pk=self.bb_sku).select_subclasses().first()
        if not product:
            raise Exception('no product found for ' + self.bb_sku)
        return product

    def get_product_filter(self) -> ProductFilter:
        model_type = type(self.get_subclass_instance())
        return Sorter(model_type).product_filter

    def get_priced(self):
        return SupplierProductMiniSerializer(self.product.in_store_priced(), many=True).data

    def get_stock_details(self) -> DetailListItem:
        details_list = [{'term': attr[0], 'values': attr[1]} for attr in self.product.attribute_list() if attr[1]]
        return details_list

    def get_subclass_remaining(self):
        remaining_list = []
        model_fields = type(self.get_subclass_instance()).get_fields(include_parents=False)
        model_fields = [field.verbose_name for field in model_fields]
        bool_attributes = self.get_bool_attributes()
        fields_to_check = [field for field in model_fields if field not in bool_attributes]
        for attr in fields_to_check:
            value = getattr(self.product, attr)
            if value:
                val_dict = {
                    'term': attr,
                    'value': value
                }
                remaining_list.append(val_dict)
        return remaining_list

    def get_bool_attributes(self):
        attributes = []
        filter_bools = self.get_product_filter().bool_groups
        for group in filter_bools:
            group_attrs = group.get('values', None)
            if group_attrs:
                attributes = attributes + group_attrs
        return attributes

    def get_bool_groups(self):
        filter_bools = self.get_product_filter().bool_groups
        groups_list = []
        for group in filter_bools:
            group_attrs = group.get('values', None)
            group_name = group.get('name', None)
            if group_attrs and group_name:
                group_vals = [{'term': attr, 'value': getattr(self.product, attr)} for attr in group_attrs]
                groups_list.append(DetailListItem(group_name, group_vals))
        return groups_list

    def assign_response(self):
        self.response.lists = [self.get_bool_groups()]
        details_list = self.get_stock_details() + self.get_subclass_remaining()
        self.response.lists.append(DetailListItem('details', details_list))
        self.response.priced = self.get_priced()
        self.response.manufacturer = self.product.manufacturer_name()
        self.response.manufacturer_url = self.product.manufacturer_url
        self.response.swatch_image = self.product.swatch_image
        self.response.room_scene = self.product.room_scene
        self.response.unit = self.product.unit

    def assign_detail_response(self):
        self.assign_response()
        detail_dict = asdict(self.response)
        self.product.detail_response = detail_dict
        self.product.save()

    def get_reponse(self):
        detail_response = self.product.detail_response
        if detail_response:
            return detail_response
        self.assign_detail_response()
        return self.product.detail_response
