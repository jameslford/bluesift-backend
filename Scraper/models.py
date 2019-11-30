import uuid
import copy
import io
import importlib
import requests
from django.conf import settings
from django.core.files import File
from django.db import models, transaction
from model_utils import Choices
from model_utils.managers import InheritanceManager
from PIL import Image as pimage
from config.local_storage import get_local_storage
from config.scripts.check_settings import exclude_production
from Products.models import Manufacturer, Product


LOCAL_STORAGE = get_local_storage()


def validate_image(image: pimage.Image):
    """ validates pillow image """
    try:
        image.verify()
        return True
    except:
        print('image wouldnt verify')
        return False


class ScraperManufacturer(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ScraperDepartment(models.Model):
    name = models.CharField(max_length=70, unique=True)

    def __str__(self):
        return self.name

    def get_module(self):
        return importlib.import_module(f'Scraper.{self.name}.add_details')

    def get_stripped_name(self):
        return self.name[7:] if self.name.startswith('Scraper') else None

    def corresponding_class(self):
        from Products.models import ProductSubClass
        stripped_name = self.get_stripped_name()
        matching_class = [cls for cls in ProductSubClass.__subclasses__() if cls.__name__ == stripped_name]
        return matching_class[0] if matching_class else None

    def name_check(self):
        if self.corresponding_class():
            return True
        return False

    def get_product_type(self):
        return self.get_module().REVISED_MODEL

    def revised_products(self):
        return ScraperBaseProduct.objects.using(
            'scraper_revised'
        ).filter(subgroup__category__department=self).select_subclasses()

    def check_sub_classes(self):
        # revised_model = self.get_module().REVISED_MODEL
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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.base_scraping_url = self.base_scraping_url.replace(' ', '')
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    # the 4 or 5 methods below could potentially be moved to subscraperbase - unesscessarry pinging back and
    # forth if no work is done in manufacturer root

    def get_module(self):
        return importlib.import_module(f'Scraper.{self.category.department.name}.{self.manufacturer.name}')

    def get_data(self):
        mod = self.get_module()
        mod.Scraper(self).get_data()

    def get_detail(self):
        mod = self.get_module()
        mod.Scraper(self).get_detail()

    @transaction.atomic()
    def run_stock_clean(self):
        self.run_special_cleaner()
        self.lower_and_strip()
        self.cleaned = True
        self.save()

    def run_special_cleaner(self):
        mod = self.get_module()
        scraper = mod.Scraper
        products = self.get_products()
        if not products:
            return
        if 'clean' in dir(scraper):
            print('clean in dir')
            mod.Scraper(self).clean()

    def lower_and_strip(self):
        products = self.get_products()
        if not products:
            return
        for product in products:
            for field in self.get_variable_fields():
                value = getattr(product, field, None)
                if value:
                    setattr(product, field, value.strip().lower())
                    product.save()

    def get_variable_fields(self):
        prod_type = self.get_prod_type()
        return prod_type.variable_fields()

    def get_prod_type(self, db='scraper_revised'):
        # pylint: disable=no-member
        products = ScraperBaseProduct.objects.filter(subgroup=self).select_subclasses()
        if not products:
            return None
        return type(products.first())

    def get_products(self):
        prod_type = self.get_prod_type()
        if prod_type:
            return prod_type.objects.filter(subgroup=self)
        return None


class ScraperBaseProduct(models.Model):
    name = models.CharField(max_length=1000)
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
        exclude_production()
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
            image_name = f'local_{str(self.manufacturer_sku)}.png'
            image: pimage.Image = self.download_image(url)
            if not image:
                continue
            buffer = io.BytesIO()
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
            image: pimage.Image = pimage.open(io.BytesIO(respone.content))
            image = image.convert('RGB')
        except (OSError, ValueError):
            print('cannot identify image file for ' + self.name)
            return None
        image_copy = copy.copy(image)
        if not validate_image(image_copy):
            print('not valid image')
            return None
        return image


    def get_final_images(self, update=False):
        exclude_production()
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
            images_name = str(self.manufacturer_sku) + '.jpg'
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

    """ superclass for subclasses in each scrapermanufacturers init modules.
    simply grants them access to standardized methods mainly for retrieving functions from submodules """

    def __init__(self, subgroup: ScraperSubgroup):
        self.subgroup = subgroup

    def get_sub_function(self, product, item: dict = None):

        """ called from the subclass in the init module of a departments
        manufacturers, i.e. 'scraperfinishsurfaces.shaw'. Will get a function specific to scraping data
        for the self.subgroup - standard for any manufacturer with more than 1 category,
        i.e shaw.laminate and shaw.hardwood """

        sub_mod = self.get_sub_module()
        func = getattr(sub_mod, 'get_special', None)
        if func:
            return func(product, item)
        return product

    def get_sub_detail(self):

        """ niche function for returning a function needed by subgroups who have to do a second pass on the data.
        i.e. gather intial data with specific urls, then reiterate on those products using urls to gather more """

        sub_mod = self.get_sub_module()
        func = getattr(sub_mod, 'get_special_detail', None)
        return func

    def get_clean_func(self):

        """ returns a function for self.subgroup that is specifcally for cleaning that subgroup.
        if function not present, will return None """

        sub_mod = self.get_sub_module()
        func = getattr(sub_mod, 'clean', None)
        return func

    def get_sub_module(self):

        """ returns a module specific to self.subgroup. i.e scraperfinishsurface.amrstrong.commercial_hardwood """ 

        current_module = f'Scraper.{self.subgroup.category.department.name}.{self.subgroup.manufacturer.name}'
        return importlib.import_module(f'.{self.subgroup.category.name}', current_module)

    def get_sub_response(self):

        """ for use in subgroups that have a require a lengthy request (using headers, post, etc..) that are not
        able to be contained in the subgroups base url. Response is obtained in subgroups submodule and
        this function returns that response """

        sub_mod = self.get_sub_module()
        func = getattr(sub_mod, 'api_response')
        return func(self.subgroup.base_scraping_url)
