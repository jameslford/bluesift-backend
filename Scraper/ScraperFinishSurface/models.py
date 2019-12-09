from django.db import models
from Scraper.models import ScraperBaseProduct


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

    def __str__(self):
        return self.name

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
            'lrv',
            'cof',
            'width',
            'length',
            'thickness',
            'label_color'
        ]

    def get_name(self):
        name = (
            f'{self.subgroup.manufacturer.name}_{self.material}_{self.sub_material}_{self.manufacturer_collection}_'
            f'{self.manufacturer_style}_{self.finish}_{self.width}x{self.length}x{self.thickness}'
        )
        return name

    def name_sku_check(self):
        if not self.manufacturer_sku:
            print('no sku')
            return
        existing_product = ScraperFinishSurface.objects.using('scraper_default').filter(
            manufacturer_sku=self.manufacturer_sku).first()
        if not existing_product:
            self.save(using='scraper_default')
            print(self.name)
            return
        keys = [k for k in existing_product.__dict__.keys() if '_state' not in k]
        for k in keys:
            existing_attr = getattr(existing_product, k, None)
            if existing_attr:
                continue
            new_attr = getattr(self, k, None)
            if new_attr:
                setattr(existing_product, k, new_attr)
        existing_product.save(using='scraper_default')
        print('updated ' + existing_product.name)
        return

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.get_name()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
