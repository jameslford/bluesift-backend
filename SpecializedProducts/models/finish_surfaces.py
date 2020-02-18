"""returns float measurements and labels on product details"""
import operator
import decimal
import webcolors
import trimesh
from trimesh.creation import box as tri_box
from trimesh.visual import TextureVisuals
from PIL import Image as pimage
from django.contrib.postgres.fields import DecimalRangeField
from django.db import models
from .base import ProductSubClass, Converter, Importer

class FinishSurface(ProductSubClass):
    """returns float measurements and labels on product details"""

    label_color = models.CharField(max_length=50, null=True, blank=True)
    actual_color = models.CharField(max_length=50, null=True, blank=True)

    # material = models.CharField(max_length=200)
    # sub_material = models.CharField(max_length=200, null=True, blank=True)
    finish = models.CharField(max_length=200, null=True, blank=True)
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
    width = DecimalRangeField(null=True, blank=True)
    length = DecimalRangeField(null=True, blank=True)

    size = models.CharField(max_length=180, null=True, blank=True)
    actual_size = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    lrv = models.CharField(max_length=60, null=True, blank=True)
    cof = models.CharField(max_length=60, null=True)

    edge = models.CharField(max_length=200, null=True, blank=True)
    end = models.CharField(max_length=200, null=True, blank=True)
    install_type = models.CharField(max_length=100, null=True)

    sqft_per_carton = models.CharField(max_length=70, null=True)
    slip_resistant = models.BooleanField(default=False)

    scale_width = models.DecimalField(decimal_places=3, null=True, blank=True, max_digits=7)
    scale_length = models.DecimalField(decimal_places=3, null=True, blank=True, max_digits=7)
    scale_thickness = models.DecimalField(decimal_places=3, null=True, blank=True, max_digits=7)

    admin_fields = [
        'scale_width',
        'scale_thickness',
        'scale_length',
        # 'walls',
        # 'countertops',
        # 'floors',
        # 'cabinet_fronts',
        # 'shower_floors',
        # 'shower_walls',
        # 'exterior_walls',
        # 'exterior_floors',
        # 'covered_walls',
        # 'covered_floors',
        # 'pool_linings',
        # 'bullnose',
        # 'covebase',
        # 'corner_covebase',
        'finish',
        # 'surface_coating',
        'look',
        # 'shade_variation'
        ]

    name_fields = [
        'look',
        'finish',
        ]

    def grouped_fields(self):
        return {
            'details': {
                'label_color': self.label_color,
                'finish': self.finish,
                'look': self.look,
                'shade_variation': self.shade_variation,
                'lrv': self.lrv,
                'cof': self.cof,
                'edge': self.edge,
                'end': self.end,
                'install_type': self.install_type,
                'sqft_per_carton': self.sqft_per_carton,
                'slip_resistant':self.slip_resistant
                },
            'size_and_shaped': {
                'thickness': self.thickness,
                'width': self.width.lower if self.width else None,
                'length': self.length.lower if self.length else None,
                'size': self.size,
                'square_inches': self.actual_size,
                },
            'applications': {
                'walls': self.walls,
                'countertops': self.countertops,
                'floors': self.floors,
                'cabinet_fronts': self.cabinet_fronts,
                'shower_floors': self.shower_floors,
                'shower_walls': self.shower_walls,
                'exterior_walls': self.exterior_walls,
                'exterior_floors': self.exterior_floors,
                'covered_walls': self.covered_walls,
                'covered_floors': self.covered_floors,
                'pool_linings': self.pool_linings,
                'bullnose': self.bullnose,
                'covebase': self.covebase,
                'corner_covebase': self.corner_covebase
            }
        }

    def assign_size(self):
        """returns float measurements and labels on product details"""
        if not (self.length and self.width):
            self.actual_size = None
            return
        if self.actual_size:
            print(self.bb_sku, 'has size')
        print('assigning size to ', self.bb_sku)
        for dim in [self.width, self.length]:
            lower = dim.lower
            upper = dim.upper
            if not lower:
                self.actual_size = None
                return
            if upper is not None:
                self.actual_size = None
                self.size = 'continous'
                return
        length = self.length.lower
        width = self.width.lower
        try:
            actual_size = length * width
            actual_size = round(actual_size, 2)
            self.actual_size = decimal.Decimal(actual_size)
        except (ValueError, TypeError):
            self.actual_size = None
        return


    def set_actual_color(self):
        """returns float measurements and labels on product details"""
        # pylint: disable=no-member
        image = self.swatch_image
        print('getting actual color for ', self.manufacturer.label, self.manufacturer_collection)
        if not image:
            return
        try:
            image = pimage.open(image)
        except OSError:
            self.delete()
            return
        try:
            image = image.convert('P', palette=pimage.ADAPTIVE, colors=1)
        except ValueError:
            return
        image = image.convert('RGB')

        colors = image.getcolors()
        first_color = max(colors, key=operator.itemgetter(0))[1]
        real_color = webcolors.rgb_to_hex(first_color)
        self.actual_color = real_color
        self.save()

    def get_height(self):
        if self.scale_thickness:
            return float(self.scale_thickness)
        return float(self.thickness) if self.thickness else 0

    def get_width(self):
        if self.scale_length:
            return float(self.scale_length)
        if self.length:
            if self.length.lower:
                return float(self.length.lower)
            return float(self.length.upper) if self.length.upper else 0
        return 0
        # return float(self.length.lower) if self.length else 0

    def get_depth(self):
        if self.scale_width:
            return float(self.scale_width)
        if self.width:
            if self.width.lower:
                return float(self.width.lower)
            return float(self.width.upper) if self.width.upper else 0
        return float(self.width.lower) if self.width else 0

    def get_texture_map(self):
        return self.tiling_image if self.tiling_image else self.swatch_image

    def convert_geometries(self):
        converter = FinishSurfaceConverter(self)
        converter.convert()


class FinishSurfaceConverter(Converter):

    def convert(self):
        return
        # if self.product.derived_gbl:
        #     print('already got glb for ', self.product.bb_sku)
        #     return
        # width = self.product.get_width()
        # depth = self.product.get_depth()
        # height = self.product.get_height()
        # image = self.product.get_texture_map()
        # if not image:
        #     print('np image for ', self.product.manufacturer.label, self.product.manufacturer_collection)
        #     return
        # image = self.product.get_texture_map().open('r')
        # image = pimage.open(image)
        # visual = TextureVisuals(image=image)
        # box: trimesh.Trimesh = tri_box((width, depth, height), visual=visual)
        # scene = box.scene()
        # self.product.save_derived_glb(scene)


class TileAndStone(FinishSurface):
    shape = models.CharField(max_length=40, null=True, blank=True)
    material_type = models.CharField(max_length=40, null=True, blank=True)

    def assign_shape(self):
        if not self.shape:
            if not self.actual_size:
                return
            ratio = self.width.lower / self.length.lower
            if ratio < .9 or ratio > 1.2:
                self.shape = 'rectangle'
                return
            self.shape = 'square'

    class Meta:
        verbose_name_plural = 'tile and stone'


class Hardwood(FinishSurface):
    composition = models.CharField(max_length=20, null=True, blank=True)
    species = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'hardwood'

class LaminateFlooring(FinishSurface):
    surface_coating = models.CharField(max_length=80, null=True, blank=True)
    species = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'laminate flooring'

class Resilient(FinishSurface):
    surface_coating = models.CharField(max_length=80, null=True, blank=True)
    shape = models.CharField(max_length=20, null=True, blank=True)
    material_type = models.CharField(max_length=20, null=True, blank=True)

    def assign_shape(self):
        """returns float measurements and labels on product details"""
        if not self.shape:
            if not self.actual_size:
                self.shape = 'continuous'
                return
            ratio = self.width.lower / self.length.lower
            if ratio < .9 or ratio > 1.2:
                self.shape = 'rectangle'
                return
            self.shape = 'square'


class CabinetLaminate(FinishSurface):

    class Meta:
        verbose_name_plural = 'cabinet laminate'
