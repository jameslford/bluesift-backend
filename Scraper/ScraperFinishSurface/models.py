import operator
import webcolors
from PIL import Image as pimage
from django.db import models
from ..models import ScraperBaseProduct


class ScraperFinishSurface(ScraperBaseProduct):

    material = models.CharField(max_length=200, blank=True, null=True)
    sub_material = models.CharField(max_length=200, blank=True, null=True)
    finish = models.CharField(max_length=200, blank=True, null=True)
    look = models.CharField(max_length=200, blank=True, null=True)
    surface_coating = models.CharField(max_length=200, blank=True, null=True, default='')
    shade_variation = models.CharField(max_length=100, blank=True, null=True, default='')
    shape = models.CharField(max_length=60, null=True, blank=True)

    actual_color = models.CharField(max_length=50, null=True, blank=True)
    label_color = models.CharField(max_length=50, null=True, blank=True)

    edge = models.CharField(max_length=200, null=True, blank=True)
    end = models.CharField(max_length=200, null=True, blank=True)

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

    thickness = models.CharField(max_length=50, blank=True, null=True)
    width = models.CharField(max_length=50, blank=True, null=True)
    length = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=30, blank=True, null=True)

    lrv = models.CharField(max_length=60, null=True, blank=True)
    cof = models.CharField(max_length=60, null=True, blank=True)

    install_type = models.CharField(max_length=100, null=True, blank=True)
    sqft_per_carton = models.CharField(max_length=70, null=True, blank=True)
    slip_resistant = models.BooleanField(default=False)

    web_id = models.CharField(max_length=200, null=True, blank=True)

    @classmethod
    def variable_fields(cls):
        return [
            'material',
            'sub_material',
            'finish',
            'look',
            'shape',
            'shade_variation',
            'surface_coating',
            'edge',
            'end',
            'install_type',
            'sqft_per_carton',
            'width',
            'length',
            'thickness',
            'label_color'
        ]

    def name_sku_check(self, update=False):
        name = (
            f'{self.subgroup.manufacturer.name}_{self.subgroup.category.name}_'
            f'{self.manufacturer_sku}_{self.material}_{self.manufacturer_collection}_'
            f'{self.manufacturer_style}_{self.finish}_{self.width}x{self.length}x{self.thickness}_'
            f'{self.end}_{self.edge}_{self.install_type}'
        )

        check_self = ScraperFinishSurface.objects.using('scraper_default').filter(name=name).first()
        if check_self:
            if update:
                check_self = self
                return check_self
            print('name exist')
            return None
        check_sku = ScraperFinishSurface.objects.using('scraper_default').filter(manufacturer_sku=self.manufacturer_sku).first()
        if self.manufacturer_sku and check_sku:
            print('sku exist - ' + check_sku.name)
            return None
        if not self.swatch_image_original:
            print('no image')
            return None
        self.name = name
        print(self.name)
        self.save()
        return self

    def set_actual_color(self):
        image = self.product.swatch_image
        if not image:
            return
        try:
            image = pimage.open(image)
        except OSError:
            print('deleting ' + self.name + 'from set_actual_color')
            self.delete()
            return
        try:
            image = image.convert('P', palette=pimage.ADAPTIVE, colors=1)
        except ValueError:
            print('unable')
            return
        image = image.convert('RGB')

        colors = image.getcolors()
        first_percentage, first_color = max(colors, key=operator.itemgetter(0))
        real_color = webcolors.rgb_to_hex(first_color)
        self.actual_color = real_color
        self.save()

