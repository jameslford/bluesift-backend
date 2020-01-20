import operator
import decimal
import webcolors
import requests
from PIL import Image as pimage
from django.contrib.postgres.fields import DecimalRangeField
from django.db import models
from Products.models import ProductSubClass
from Products.serializers import serialize_geometry
from .serializers import AdminFields


class FinishSurface(ProductSubClass):

    label_color = models.CharField(max_length=50, null=True, blank=True)
    actual_color = models.CharField(max_length=50, null=True, blank=True)

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
    width = DecimalRangeField(null=True, blank=True)
    length = DecimalRangeField(null=True, blank=True)


    size = models.CharField(max_length=180, null=True, blank=True)
    actual_size = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    shape = models.CharField(max_length=80, null=True, blank=True)

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
        'corner_covebase',
        'material',
        'sub_material',
        'finish',
        'surface_coating',
        'look',
        'shade_variation'
        ]

    def serialize(self):
        main = self.serialize_remaining()
        main.update(self.serialize_size())
        main.update(self.serialize_applications())
        return main

    def serialize_special(self):
        return {
            'details': self.serialize_remaining(),
            'size_and_shape': self.serialize_size(),
            'applications': self.serialize_applications(),
        }

    def serialize_remaining(self):
        return {
            'label_color': self.label_color,
            'material': self.material,
            'sub_material': self.sub_material,
            'finish': self.finish,
            'surface_coating': self.surface_coating,
            'look': self.look,
            'shade_variation': self.shade_variation,
            'lrv': self.lrv,
            'cof': self.cof,
            'edge': self.edge,
            'end': self.end,
            'install_type': self.install_type,
            'sqft_per_carton': self.sqft_per_carton,
            'slip_resistant':self.slip_resistant
            }

    def serialize_size(self):
        return {
            'thickness': self.thickness,
            'width': self.width.lower if self.width else None,
            'length': self.length.lower if self.length else None,
            'size': self.size,
            'square inches': self.actual_size,
            'shape': self.shape
        }

    def serialize_applications(self):
        return {
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


    def assign_size(self):
        if not (self.length and self.width):
            self.actual_size = None
            return
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

    def assign_shape(self):
        if not self.shape:
            if not self.actual_size:
                self.shape = 'continuous'
                return
            print('actual size', self.actual_size)
            ratio = self.width.lower / self.length.lower
            if ratio < .9 or ratio > 1.2:
                self.shape = 'rectangle'
                return
            self.shape = 'square'

    def set_actual_color(self):
        # pylint: disable=no-member
        image = self.swatch_image
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
        first_color = max(colors, key=operator.itemgetter(0))[1]
        real_color = webcolors.rgb_to_hex(first_color)
        self.actual_color = real_color
        self.save()

    def name_fields(self):
        return [
            'material',
            'look',
            'finish',
            'sub_material',
            'surface_coating'
            ]

    def geometries(self):
        if self.scale_length:
            length = self.scale_length
        else:
            length = self.length.lower if self.length else None
        if self.scale_width:
            width = self.scale_width
        else:
            width = self.width.lower if self.width else None
        if self.scale_thickness:
            thickness = self.scale_thickness
        else:
            thickness = self.thickness

        return {
            'width': width,
            'length': length,
            'thickness': thickness
            }

    def convert_objects(self):
        url = 'http://localhost:5001/encoded-joy-257818/us-central1/helloWorld'
        data = serialize_geometry(self)
        r = requests.get(url, params=data)
        print(r.text)


    def get_admin_fields(self):
        return AdminFields(self).data

        # return {
        #     'scale_width',
        #     'scale_thickness',
        #     'scales_length',
        #     'walls',
        #     'countertops',
        #     'floors',
        #     'cabinet_fronts',
        #     'shower_floors',
        #     'shower_walls',
        #     'exterior_walls',
        #     'exterior_floors',
        #     'covered_walls',
        #     'covered_floors',
        #     'pool_linings',
        #     'bullnose',
        #     'covebase',
        #     'corner_covebase',
        #     'material',
        #     'sub_material',
        #     'finish',
        #     'surface_coating',
        #     'look',
        #     'shade_variation',
        # }
    # def create_obj_file(self):
    #     if not (
    #         self.width and
    #         self.length and
    #         self.width.lower
    #         and self.length.lower
    #         and self.thickness):
    #         return
    #     width = self.width.lower
    #     length = self.length.lower
    #     thick = self.thickness

    #     # create x, y, z arrays for vertices
    #     whalf = width/2
    #     lhalf = length/2

    #     blb = ((0-whalf), 0, (0-lhalf))
    #     brb = (whalf, 0, (0-lhalf))
    #     blf = ((0-whalf), 0, lhalf)
    #     brf = (whalf, 0, lhalf)

    #     tlb = ((0-whalf), thick, (0-lhalf))
    #     trb = (whalf, thick, (0-lhalf))
    #     tlf = ((0-whalf), thick, lhalf)
    #     trf = (whalf, thick, lhalf)




# class Appliance(ProductSubClass):
#     room_type = models.CharField(max_length=100, blank=True, null=True)
#     appliance_type = models.CharField(max_length=100, blank=True, null=True)
#     height = models.DecimalField(max_digits=5, decimal_places=2)
#     depth = models.DecimalField(max_digits=5, decimal_places=2)
#     width = models.DecimalField(max_digits=5, decimal_places=2)


# class Millwork(ProductSubClass):
#     pass
