# from django.db import models
from django.contrib.gis.db import models
from django.db.models import Min
from django.contrib.gis.geos import MultiPoint
import io
from PIL import Image as pimage, ImageFilter, ImageEnhance

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


class Material(models.Model):
    label = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.label


class Finish(models.Model):
    material = models.ForeignKey(
        Material,
        null=True,
        related_name='finishes',
        on_delete=models.SET_NULL,
        )
    label = models.CharField(max_length=60)

    class Meta:
        unique_together = (('material', 'label'))

    def __str__(self):
        return self.label


class SurfaceTexture(models.Model):
    material = models.ForeignKey(
        Material,
        null=True,
        related_name='textures',
        on_delete=models.SET_NULL,
        )

    label = models.CharField(max_length=60)

    class Meta:
        unique_together = (('material', 'label'))

    def __str__(self):
        return self.label


class SubMaterial(models.Model):
    material = models.ForeignKey(
        Material,
        null=True,
        related_name='subs',
        on_delete=models.SET_NULL,
        )

    label = models.CharField(max_length=60)

    class Meta:
        unique_together = (('material', 'label'))

    def __str__(self):
        return self.label


class SurfaceCoating(models.Model):
    material = models.ForeignKey(
        Material,
        null=True,
        related_name='coatings',
        on_delete=models.SET_NULL,
        )

    label = models.CharField(max_length=60)

    class Meta:
        unique_together = (('material', 'label'))

    def __str__(self):
        return self.label


class Look(models.Model):
    label = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.label

class Edge(models.Model):
    label = models.CharField(max_length=60, unique=True)

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
    bb_sku = models.CharField(max_length=500, unique=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        null=True,
        related_name='products',
        on_delete=models.SET_NULL,
        )

    manufacturer_url = models.URLField(null=True, blank=True)
    manufacturer_sku = models.CharField(max_length=50, null=True, blank=True)
    manu_collection = models.CharField(max_length=200, null=True, blank=True)
    manufacturer_color = models.CharField(max_length=200, null=True)

    actual_color = models.CharField(max_length=60, null=True)

    swatch_image = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
        related_name='swatches'
        )
    room_scene = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
        related_name='room_scenes'
        )
    tiling_image = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
        related_name='tiling_images'
        )

    last_scraped = models.DateTimeField(null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True)

    # categorized
    material = models.ForeignKey(
        Material,
        null=True,
        on_delete=models.SET_NULL
        )
    sub_material = models.ForeignKey(
        SubMaterial,
        null=True,
        on_delete=models.SET_NULL
        )   
    finish = models.ForeignKey(
        Finish,
        null=True,
        on_delete=models.SET_NULL,
        )
    surface_texture = models.ForeignKey(
        SurfaceTexture,
        null=True,
        on_delete=models.SET_NULL
        )
    surface_coating = models.ForeignKey(
        SurfaceCoating,
        null=True,
        on_delete=models.SET_NULL
        )

    # application
    walls = models.BooleanField(default=False)
    countertops = models.BooleanField(default=False)
    floors = models.BooleanField(default=False)
    cabinet_fronts = models.BooleanField(default=False)
    shower_floors = models.BooleanField(default=False)
    shower_walls = models.BooleanField(default=False)
    exterior_walls = models.BooleanField(default=False)
    exterior_floors = models.BooleanField(default=False)
    covered_walls = models.BooleanField(default=False)
    covered_floors = models.BooleanField(default=False)
    pool_linings = models.BooleanField(default=False)
    bullnose = models.BooleanField(default=False)
    covebase = models.BooleanField(default=False)
    corner_covebase = models.BooleanField(default=False)

    thickness = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    width = models.CharField(max_length=50, null=True, blank=True)
    length = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=30, null=True)

    look = models.ForeignKey(Look, null=True, on_delete=models.SET_NULL)

    lrv = models.CharField(max_length=60, null=True, blank=True)
    cof = models.CharField(max_length=60, null=True)

    residential_warranty = models.CharField(max_length=100, null=True, blank=True)
    commercial_warranty = models.CharField(max_length=100, null=True, blank=True)
    light_commercial_warranty = models.CharField(max_length=100, null=True)

    install_type = models.CharField(max_length=100, null=True)
    commercial = models.BooleanField(default=False)
    sqft_per_carton = models.CharField(max_length=70, null=True)
    slip_resistant = models.BooleanField(default=False)
    shade = models.CharField(max_length=60, null=True)

    shade_variation = models.ForeignKey(
        ShadeVariation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
        )

    edge = models.ForeignKey(
        Edge,
        null=True,
        on_delete=models.SET_NULL
    )

    notes = models.TextField(null=True, blank=True)

    lowest_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True
        )
    for_sale_online = models.BooleanField(default=False)
    for_sale_in_store = models.BooleanField(default=False)

    # location
    locations = models.MultiPointField(null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        cats = [
            self.sub_material,
            self.finish,
            self.surface_texture,
            self.surface_coating
            ]
        for cat in cats:
            if not cat:
                continue
            if cat.material != self.material:
                return
        # self.resize_image()
        super(Product, self).save(*args, **kwargs)

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
        # self.resize_image()
        self.save()
        return

    def set_locations(self):
        self.locations = None
        in_store_sellers = self.priced.filter(for_sale_in_store=True)
        if in_store_sellers.count() > 0:
            coordinates = [q.supplier.address.coordinates.get_point() for q in in_store_sellers]
            points = MultiPoint(*coordinates)
            self.locations = points
            self.save()

    def resize_image(self):
        from django.conf import settings
        desired_size = settings.DESIRED_IMAGE_SIZE
        if not self.swatch_image:
            self.delete()
            print('wtf')
            return
        image = self.swatch_image.image
        image = pimage.open(image)
        buffer = io.BytesIO()
        print('hello')
        # w, h = image.size
        # if w == desired_size and h <= desired_size:
        #     return
        # w_ratio = desired_size/w
        # height_adjust = int(round(h * w_ratio))
        # image = image.resize((desired_size, height_adjust))
        # if image.size[1] > desired_size:
        #     image = image.crop((
        #         0,
        #         0,
        #         desired_size,
        #         desired_size
        #         ))
        # image.save(buffer, 'JPEG')
        # image_name = self.swatch_image.original_url.split('/')[-1] + '.jpg'
        # self.swatch_image.image.save(image_name, buffer)
        if self.tiling_image:
            self.tiling_image.delete()
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.0)
        # enhancer = ImageEnhance.Sharpness(image)
        # image = enhancer.enhance(2.0)
        # image = image.filter(ImageFilter.SHARPEN)
        # image = image.filter(ImageFilter.MedianFilter())
        # image = image.filter(ImageFilter.FIND_EDGES)
        # image.convert
        image.save(buffer, 'JPEG')
        new_name = self.name.replace(' ', '') + '_tiling.jpg'
        tile_image = Image(original_url=new_name)
        tile_image.image.save(new_name, buffer)
        tile_image.save()
        print(buffer)
        self.tiling_image = tile_image
        self.save()

    def manufacturer_name(self):
        return self.manufacturer.label

    def set_size(self):
        if not self.size:
            self.size = self.width + 'x' + self.length

    def actual_image(self):
        return self.image.image
