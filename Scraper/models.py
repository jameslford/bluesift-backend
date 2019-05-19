import uuid
import copy
import io
from io import BytesIO
import importlib
import requests
from django.conf import settings
from django.core.files import File
from django.db import models
from model_utils import Choices
from model_utils.managers import InheritanceManager
from PIL import Image as pimage
from config.settings.local_storage import get_local_storage
from config.scripts.check_settings import check_local
from Products.models import Manufacturer, Product


LOCAL_STORAGE = get_local_storage()


class ScraperManufacturer(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ScraperDepartment(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name

    def get_module(self):
        return importlib.import_module(f'Scraper.{self.name}.add_details')

    def get_stripped_name(self):
        if self.name.startswith('Scraper'):
            return self.name[7:]
        return None

    def corresponding_class(self):
        from config.scripts.globals import PRODUCT_SUBCLASSES
        stripped_name = self.get_stripped_name()
        if stripped_name:
            return PRODUCT_SUBCLASSES.get(stripped_name, None)
        return None

    def name_check(self):
        if self.corresponding_class():
            return True
        return False

    def revised_products(self):
        return ScraperBaseProduct.objects.using(
            'scraper_revised'
        ).filter(subgroup__category__department=self).select_subclasses()

    def check_sub_classes(self):
        revised_model = self.get_module().REVISED_MODEL
        new_model = self.get_module().NEW_MODEL
        if new_model != self.corresponding_class():
            raise Exception('wrong class in department submodule or globals for ' + self.name)

    def add_to_default(self):
        self.check_sub_classes()
        corresponding_class = self.corresponding_class()
        for revised_product in self.revised_products():
            bb_sku = revised_product.bb_sku
            revised_manufacturer_name = revised_product.subgroup.manufacturer.name
            new_product = corresponding_class.objects.get_or_create(bb_sku=bb_sku)[0]
            manufacturer = Manufacturer.objects.get_or_create(label=revised_manufacturer_name)[0]
            new_product.manufacturer = manufacturer
            new_product.manufacturer_url = revised_product.product_url
            new_product.manufacturer_sku = revised_product.manufacturer_sku
            new_product.manu_collection = revised_product.manufacturer_collection
            new_product.manufacturer_style = revised_product.manufacturer_style
            new_product.unit = Product.SF
            new_product.swatch_image = revised_product.swatch_image_final
            new_product.room_scene = revised_product.room_scene_final
            new_product.tiling_image = revised_product.tiling_scene_final
            new_product.commercial_warranty = revised_product.commercial_warranty
            new_product.residential_warranty = revised_product.residential_warranty
            new_product.light_commercial_warranty = revised_product.light_commericial_warranty
            self.get_module().add_details(new_product, revised_product)


    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name_check():
            raise Exception('Department name does not conform to <Scraper<corresponding_class>>')
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class ScraperCategory(models.Model):
    UNITS = Choices('SF', 'Each')
    name = models.CharField(max_length=70)
    unit = models.CharField(choices=UNITS, default=UNITS.SF, max_length=10)
    department = models.ForeignKey(
        ScraperDepartment,
        related_name='categories',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.department.name}_{self.name}'


class ScraperSubgroup(models.Model):
    manufacturer = models.ForeignKey(
        ScraperManufacturer,
        related_name='subgroup',
        on_delete=models.CASCADE
        )
    category = models.ForeignKey(
        ScraperCategory,
        related_name='subgroup',
        on_delete=models.CASCADE
    )
    base_scraping_url = models.URLField(max_length=2000, blank=True)
    scraped = models.BooleanField(default=False)
    cleaned = models.BooleanField(default=False)

    class Meta:
        unique_together = ('manufacturer', 'category')

    def __str__(self):
        return f'{self.manufacturer.name}_{self.category.name}'

    def get_module(self):
        return importlib.import_module(f'Scraper.{self.category.department.name}.{self.manufacturer.name}')

    def get_data(self):
        mod = self.get_module()
        mod.Scraper(self).get_data()

    def get_detail(self):
        mod = self.get_module()
        mod.Scraper(self).get_detail()

    def run_stock_clean(self):
        mod = self.get_module()
        mod.Scraper(self)

    def get_variable_fields(self):
        prod_type = self.get_prod_type()
        return prod_type.variable_fields()

    def get_prod_type(self):
        # pylint: disable=no-member
        product = self.products.select_subclasses().first()
        return type(product)

    def get_products(self):
        prod_type = self.get_prod_type()
        return prod_type.objects.filter(subgroup=self)


class ScraperBaseProduct(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    manufacturer_sku = models.CharField(max_length=200, null=True, blank=True, unique=True)
    manufacturer_collection = models.CharField(max_length=200, blank=True)
    manufacturer_style = models.CharField(max_length=200, blank=True)
    product_url = models.URLField(max_length=500, default='')

    swatch_image_original = models.URLField(blank=True, max_length=500)
    room_scene_original = models.URLField(blank=True, null=True, max_length=500)
    tiling_scene_original = models.URLField(blank=True, null=True, max_length=500)

    swatch_image_local = models.ImageField(null=True, storage=LOCAL_STORAGE, upload_to='swatches/')
    room_scene_local = models.ImageField(null=True, storage=LOCAL_STORAGE, upload_to='rooms/')
    tiling_scene_local = models.ImageField(null=True, storage=LOCAL_STORAGE, upload_to='tiles/')

    swatch_image_final = models.ImageField(null=True, upload_to='swatches/')
    room_scene_final = models.ImageField(null=True, upload_to='rooms/')
    tiling_scene_final = models.ImageField(null=True, upload_to='tiles/')

    residential_warranty = models.CharField(blank=True, max_length=200, default='', null=True)
    commercial_warranty = models.CharField(blank=True, max_length=200, default='', null=True)
    light_commericial_warranty = models.CharField(blank=True, max_length=200, default='', null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_modiefied = models.DateTimeField(auto_now=True)

    commercial = models.BooleanField(default=False)

    subgroup = models.ForeignKey(
        ScraperSubgroup,
        null=True,
        blank=True,
        related_name='products',
        on_delete=models.SET_NULL
    )
    bb_sku = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    objects = InheritanceManager()

    def manufacturer_name(self):
        return self.subgroup.manufacturer.name

    def category_name(self):
        return self.subgroup.category.name

    def department_name(self):
        return self.subgroup.category.department.name


    def get_local_images(self, update=False):
        check_local()
        images = [
            [self.swatch_image_original, self.swatch_image_local],
            [self.room_scene_original, self.room_scene_local],
            [self.tiling_scene_original, self.tiling_scene_local]
        ]
        for img_group in images:
            if not img_group[0]:
                continue
            url = img_group[0]
            destination = img_group[1]
            if not update and destination:
                print('already got')
                continue
            image_name = f'local_{str(self.bb_sku)}.png'
            image: pimage.Image = self.download_image(url)
            if not image:
                # print('bad image')
                continue
            buffer = BytesIO()
            image.save(buffer, 'PNG', optimize=True)
            destination.save(image_name, File(buffer), save=False)
            print('getting local for ' + self.name)
            self.save()

    def download_image(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
        respone = requests.get(url, headers=headers)
        if not respone.status_code == 200:
            print('bad request')
            return None
        try:
            image: pimage.Image = pimage.open(BytesIO(respone.content))
            image = image.convert('RGB')
        except (OSError, ValueError):
            print('cannot identify image file for ' + self.name)
            return None
        image_copy = copy.copy(image)
        if not self.validate_image(image_copy):
            print('not valid image')
            return None
        return image

    def validate_image(self, image: pimage.Image):
        try:
            image.verify()
            return True
        except:
            print('image wouldnt verify')
            return False

    def get_final_images(self, update=False):
        check_local()
        img_groups = [
            [self.swatch_image_local, self.swatch_image_final],
            [self.room_scene_local, self.room_scene_final],
            [self.tiling_scene_local, self.tiling_scene_final]
        ]
        for img_group in img_groups:
            local = img_group[0]
            destination = img_group[1]
            if not local:
                print('no local')
                continue
            if not update and destination:
                print('already got final')
                continue
            image = self.resize_image(local)
            if not image:
                print('bad image - final')
                continue
            buffer = io.BytesIO()
            try:
                image.save(buffer, 'JPEG')
            except IOError:
                print('io error')
                continue
            images_name = str(self.bb_sku) + '.jpg'
            destination.save(images_name, buffer)
            print('getting final for ' + self.name)
            self.save()


    def resize_image(self, image):
        desired_size = settings.DESIRED_IMAGE_SIZE
        try:
            image = pimage.open(image)
        except (OSError, ValueError) as e:
            print(str(e) + ' for ' + self.name)
            image = None
            self.save()
            return None
        width, height = image.size
        if width == desired_size and height <= desired_size:
            return image
        w_ratio = desired_size/width
        height_adjust = int(round(height * w_ratio))
        image = image.resize((desired_size, height_adjust))
        if image.size[1] > desired_size:
            image = image.crop((
                0,
                0,
                desired_size,
                desired_size
                ))
        return image


class ScraperAggregateProductRating(models.Model):
    rating_value = models.IntegerField()
    rating_max = models.IntegerField(default=5)
    rating_count = models.IntegerField()
    product_bbsku = models.CharField(max_length=80, unique=True)


class SubScraperBase:
    def __init__(self, subgroup: ScraperSubgroup):
        self.subgroup = subgroup

    def get_sub_function(self, product, item: dict = None):
        sub_mod = self.get_sub_module()
        func = getattr(sub_mod, 'get_special')
        return func(product, item)

    def get_sub_detail(self):
        sub_mod = self.get_sub_module()
        func = getattr(sub_mod, 'get_special_detail')
        return func

    def get_sub_module(self):
        current_module = f'Scraper.{self.subgroup.category.department.name}.{self.subgroup.manufacturer.name}'
        return importlib.import_module(f'.{self.subgroup.category.name}', current_module)

    def get_sub_response(self):
        print('getting response')
        sub_mod = self.get_sub_module()
        func = getattr(sub_mod, 'api_response')
        return func(self.subgroup.base_scraping_url)
