from django.db import models
from Products.models import Product, ProductSubClass


class FinishSurface(ProductSubClass):

    label_color = models.CharField(max_length=200, null=True, blank=True)

    material = models.CharField(max_length=200)
    sub_material = models.CharField(max_length=200, null=True, blank=True)

    finish = models.CharField(max_length=200, null=True, blank=True)
    surface_coating = models.CharField(max_length=200, null=True, blank=True)
    look = models.CharField(max_length=200, null=True, blank=True)
    shade_variation = models.CharField(max_length=200, null=True, blank=True)

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

    size = models.CharField(max_length=80, null=True, blank=True)
    shape = models.CharField(max_length=80, null=True, blank=True)

    lrv = models.CharField(max_length=60, null=True, blank=True)
    cof = models.CharField(max_length=60, null=True)

    edge = models.CharField(max_length=200, null=True, blank=True)
    end = models.CharField(max_length=200, null=True, blank=True)
    install_type = models.CharField(max_length=100, null=True)

    sqft_per_carton = models.CharField(max_length=70, null=True)
    slip_resistant = models.BooleanField(default=False)


    @staticmethod
    def bool_groups():
        return [
            {
                'name': 'applications',
                'terms': [
                    'walls',
                    'countertops',
                    'floors',
                    'cabinet_fronts',
                    'shower_floors',
                    'shower_walls',
                    'exterior_walls',
                    'exterior_floors',
                    'covered_walls',
                    'covered_floors',
                    'pool_linings',
                    'bullnose',
                    'covebase',
                    'corner_covebase'
                ]
            }
        ]

    @staticmethod
    def key_term():
        return {
            'name': 'material',
            # 'class': Material
        }

    @staticmethod
    def dependents():
        return [
            'finish',
            'sub_material',
            'surface_coating'
        ]

    @staticmethod
    def fk_standalones():
        return [
            'label_color',
            'look'
        ]

    @staticmethod
    def standalones():
        return []

    def details(self):
        return [
            ['material', self.material if self.material else None],
            ['finish', self.finish if self.finish else None],
            ['submaterial', self.sub_material if self.sub_material else None],
            ['surface_coating', self.surface_coating if self.surface_coating else None],
            ['thickness', self.thickness if self.thickness else None],
            ['width', self.width if self.width else None],
            ['length', self.length if self.length else None],
            ['edge', self.edge if self.edge else None],
        ]


    def set_size(self):
        if not self.size:
            self.size = self.width + ' x ' + self.length
