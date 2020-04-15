import io
import importlib
from django.conf import settings
from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from utils.downloads import url_to_pimage
from utils.images import resize_image
from Products.models import Manufacturer

# Create your models here.
class ScraperGroup(models.Model):
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        )
    category = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'app_label': 'SpecializedProducts'}
        )
    module_name = models.CharField(max_length=70)
    scraped = models.BooleanField(default=False)
    images_obtained = models.BooleanField(default=False)
    geometry_obtained = models.BooleanField(default=False)
    base_url = models.URLField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return f'{self.manufacturer.label}, {self.module_name}'

    def path(self):
        return f'Scraper.derivatives.{self.manufacturer.label}.{self.module_name}'

    def get_model(self):
        return self.category.model_class()

    def response(self):
        return {
            'pk': self.pk,
            'manufacturer_pk': self.manufacturer.pk,
            'manufacturer_name': self.manufacturer.label,
            'model': self.category.model,
            'module_name': self.module_name,
            'scraped': self.scraped,
            'images_obtained': self.images_obtained,
            'base_url': self.base_url
            }

    def convert_geometries(self):
        products = self.category.model_class().objects.all()
        for product in products:
            product.convert_geometries()

    def get_final_images(self, update=False):
        desired_size = settings.DESIRED_IMAGE_SIZE
        products = self.category.model_class().objects.all()
        for product in products:
            img_groups = [
                [product.swatch_image_original, product.swatch_image],
                [product.room_scene_original, product.room_scene],
                [product.tiling_image_original, product.tiling_image]
            ]
            for img_group in img_groups:
                original = img_group[0]
                destination = img_group[1]
                if not original:
                    print('no local')
                    continue
                if not update and destination:
                    print('already got final')
                    continue
                image = url_to_pimage(original)
                if not image:
                    continue
                image = image.convert('RGB')
                image = resize_image(image, desired_size)
                if not image:
                    print('unable to convert')
                    continue
                buffer = io.BytesIO()
                try:
                    image.save(buffer, 'JPEG', quality=90)
                except IOError:
                    print('io error')
                    continue
                images_name = str(product.manufacturer_sku) + '.jpg'
                destination.save(images_name, buffer, save=True)
                product.save()
                print('getting final for ' + product.manufacturer.label, product.bb_sku)

    @transaction.atomic
    def scrape(self):
        path = self.path()
        mod = importlib.import_module(path)
        mod.run(self)
        self.scraped = True
        self.save()
        self.get_final_images()
