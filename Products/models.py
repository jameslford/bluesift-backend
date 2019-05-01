# from django.db import models
import io
from PIL import Image as pimage
from model_utils.managers import InheritanceManager
from django.contrib.gis.db import models
from django.db.models import Min, Avg
from django.contrib.gis.geos import MultiPoint


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


class Image(models.Model):
    original_url = models.CharField(max_length=300, unique=True)
    image = models.ImageField(max_length=300, null=True)

    def __str__(self):
        return self.original_url


class ProductSubClass(models.Model):
    objects = InheritanceManager()


class Product(models.Model):
    SF = 'SF'
    EACH = 'EACH'
    UNIT_CHOICES = (
        (SF, 'SF'),
        (EACH, 'Each')
    )

    name = models.CharField(max_length=1200)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=SF)
    bb_sku = models.CharField(max_length=500, unique=True)
    manufacturer_url = models.URLField(max_length=300, null=True, blank=True)
    manufacturer_sku = models.CharField(max_length=200, null=True, blank=True)
    manu_collection = models.CharField(max_length=200, null=True, blank=True)
    manufacturer_style = models.CharField(max_length=200, null=True, blank=True)

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

    content = models.OneToOneField(ProductSubClass, on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)

    # content_object = models.OneToOneField(ProductSubClass, on_delete=models.CASCADE)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('content_type', 'object_id')

    manufacturer = models.ForeignKey(
        Manufacturer,
        null=True,
        related_name='products',
        on_delete=models.SET_NULL,
        )
    swatch_image = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
        related_name='swatches'
        )
    room_scene = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='room_scenes'
        )
    tiling_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tiling_images'
        )

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

    def resize_image(self):
        from django.conf import settings
        desired_size = settings.DESIRED_IMAGE_SIZE
        if not self.swatch_image:
            return
        image = self.swatch_image.image
        try:
            image = pimage.open(image)
        except OSError:
            print('deleting ' + self.name)
            self.delete()
            return
        buffer = io.BytesIO()
        w, h = image.size
        if w == desired_size and h <= desired_size:
            return
        w_ratio = desired_size/w
        height_adjust = int(round(h * w_ratio))
        image = image.resize((desired_size, height_adjust))
        if image.size[1] > desired_size:
            image = image.crop((
                0,
                0,
                desired_size,
                desired_size
                ))
        try:
            image.save(buffer, 'JPEG')
        except IOError:
            print('unable io error')
            return
        image_name = self.swatch_image.original_url.split('/')[-1] + '.jpg'
        self.swatch_image.image.save(image_name, buffer)
        self.save()
        # self.set_actual_color()

    def manufacturer_name(self):
        if not self.manufacturer:
            return None
        return self.manufacturer.label









# class ProductSubClass(models.Model):

#     _product = GenericRelation(
#         Product,
#         content_type_field='content_type',
#         object_id_field='object_id'
#         )

#     class Meta:
#         abstract = True

    # @property
    # def product(self):
    #     return self._product.first()
