import webcolors
import operator
from PIL import Image as pimage
from django.db import models
from Products.models import ProductSubClass, Product
from Colors.models import Color


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


class FinishSurface(ProductSubClass):

    actual_color = models.ForeignKey(
        Color,
        null=True,
        on_delete=models.SET_NULL,
        related_name='actuals'
        )
    label_color = models.ForeignKey(
        Color,
        null=True,
        on_delete=models.SET_NULL,
        related_name='labels'
        )
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
    look = models.ForeignKey(
        Look,
        null=True,
        on_delete=models.SET_NULL
        )
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

    lrv = models.CharField(max_length=60, null=True, blank=True)
    cof = models.CharField(max_length=60, null=True)

    install_type = models.CharField(max_length=100, null=True)
    sqft_per_carton = models.CharField(max_length=70, null=True)
    slip_resistant = models.BooleanField(default=False)
    shade = models.CharField(max_length=60, null=True)

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
            'class': Material
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
            ['material', self.material.label],
            ['finish', self.finish.label],
            ['submaterial', self.sub_material.label],
            ['surface_coating', self.surface_coating.label],
            ['thickness', self.thickness],
            ['width', self.width],
            ['length', self.length],
            ['edge', self.edge.label],
        ]

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
        super(FinishSurface, self).save(*args, **kwargs)

    def set_actual_color(self):
        swatch_image = self.product.swatch_image
        if not swatch_image:
            return
        image = swatch_image.image
        if not image:
            return
        try:
            image = pimage.open(image)
        except OSError:
            print('deleting ' + self.name + 'from set_actual_color')
            self.delete()
            return
        w, h = image.size
        from django.conf import settings
        if w > settings.DESIRED_IMAGE_SIZE:
            # self.resize_image()
            return
        divisor = 4
        image = image.crop((
            w/divisor,
            h/divisor,
            w - w/divisor,
            h - h/divisor
        ))
        try:
            image = image.convert('P', palette=pimage.ADAPTIVE, colors=1)
        except ValueError:
            print('unable')
            return
        image = image.convert('RGB')

        colors = image.getcolors()
        first_percentage, first_color = max(colors, key=operator.itemgetter(0))
        real_color, created = Color.objects.get_or_create(label=webcolors.rgb_to_hex(first_color))
        self.actual_color = real_color
        self.save()
