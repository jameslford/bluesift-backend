"""returns float measurements and labels on product details"""
import os
import operator
import json
import decimal
import base64
import pyassimp
from json.decoder import JSONDecodeError
import webcolors
import requests
from PIL import Image as pimage
from django.core.files.base import ContentFile, File
from django.contrib.postgres.fields import DecimalRangeField
from django.db import models
from Products.models import Product

class ProductSubClass(Product):
    """returns float measurements and labels on product details"""
    name_fields = []
    admin_fields = []

    class Meta:
        abstract = True

    def grouped_fields(self):
        """returns attribute groups in product detail on front end"""
        return {}

    def geometries(self):
        """returns float measurements and labels on product details"""
        return {}

    def get_width(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_height(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_depth(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_texture_map(self):
        """returns float measurements and labels on product details"""
        return None

    def conversion_geometries(self):
        from .serializers import SubproductGeometryConversionSerializer
        """returns float measurements and labels on product details"""
        return SubproductGeometryConversionSerializer(self).data

    def presentation_geometries(self):
        from .serializers import SubproductGeometryPresentationSerializer
        """returns float measurements and labels on product details"""
        return SubproductGeometryPresentationSerializer(self).data

    @classmethod
    def validate_sub(cls, sub: str):
        """returns float measurements and labels on product details"""
        return bool(sub.lower() in [klas.__name__.lower() for klas in cls.__subclasses__()])

    @classmethod
    def return_sub(cls, sub: str):
        """returns float measurements and labels on product details"""
        classes = [klas for klas in cls.__subclasses__() if klas.__name__.lower() == sub.lower()]
        if classes:
            return classes[0]
        return None



class FinishSurface(ProductSubClass):
    """returns float measurements and labels on product details"""

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

    name_fields = [
        'material',
        'look',
        'finish',
        'sub_material',
        'surface_coating'
        ]

    def grouped_fields(self):
        return {
            'details': {
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
                },
            'size_and_shaped': {
                'thickness': self.thickness,
                'width': self.width.lower if self.width else None,
                'length': self.length.lower if self.length else None,
                'size': self.size,
                'square_inches': self.actual_size,
                'shape': self.shape
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

    def set_actual_color(self):
        """returns float measurements and labels on product details"""
        # pylint: disable=no-member
        image = self.swatch_image
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
        return float(self.length.lower) if self.length else 0

    def get_depth(self):
        if self.scale_width:
            return float(self.scale_width)
        return float(self.width.lower) if self.width else 0

    def get_texture_map(self):
        if self.tiling_image:
            return self.tiling_image.url
        return self.swatch_image.url if self.swatch_image else None

    def convert_geometries(self):
        pass
        # url = self.swatch_image.url
        # image = base64.b64encode(requests.get(url).content)
        # image = f'data:image/png; base64, {image}'
        # url = 'http://localhost:5001/encoded-joy-257818/us-central1/helloWorld'
        # data = self.conversion_geometries()
        # response = requests.post(url, data=data).text
        # try:
        #     response = json.loads(response)
        # except JSONDecodeError:
        #     return
        # obj_content: str = response.get('obj_file')
        # if obj_content:
        #     name = str(self.bb_sku) + '.obj'
        #     self.derived_obj_file.save(name, ContentFile(obj_content.encode('utf-8')))
        # self.three_json = response.get('three_json')
        # self.derived_depth = response.get('derived_depth')
        # self.derived_height = response.get('derived_height')
        # self.derived_width = response.get('derived_width')
        # self.save()


class Appliance(ProductSubClass):
    appliance_type = models.CharField(max_length=100, blank=True, null=True)
    room_type = models.CharField(max_length=100, null=True, blank=True)
    width = DecimalRangeField(null=True, blank=True)
    height = DecimalRangeField(null=True, blank=True)
    depth = DecimalRangeField(null=True, blank=True)

    def convert_geometries(self):
        filetypes = [
            {
                'reference': self.derived_dae_file, 
                'ext': '.dae',
                'filetype': 'collada',
                'pp': pyassimp.postprocess.aiProcessPreset_TargetRealtime_MaxQuality
            },
            {
                'reference': self.derived_gltf_file,
                'ext': '.gltf',
                'filetype': 'gltf2',
                'pp': pyassimp.postprocess.aiProcessPreset_TargetRealtime_Fast
                },
        ]
        request = requests.get(self.obj_file.url)
        file_obj = ContentFile(request.content)
        obj = pyassimp.load(file_obj, 'obj')
        for ft in filetypes:
            filename = self.name + ft['ext']
            print(filename, ' running')
            pyassimp.export(obj, filename, ft['filetype'], )
            print('pyassimp exported ', filename)
            cwd = os.getcwd()
            print(cwd)
            cwd_files = os.listdir(cwd)
            for cwd_file in cwd_files:
                print(cwd_file)
                if filename in cwd_file:
                    new_file = open(cwd_file, 'rb')
                    self.geometry_clean = True
                    ft['reference'].save(filename, File(new_file), save=True)
                    print(ft['filetype'] + ' created')
                    os.remove(cwd_file)
                    break


        # path = os.getcwd() + self.name + '.obj'
        # print(path)
        # with open(path, 'wb') as f:
        #     f.write(request.content)

        # file_obj = ContentFile(request.text.encode('utf-8'))
        # print(file_obj.file)

        # self.derived_dae_file.save(filename, ContentFile(dae_content.encode('utf-8')))
        # pyassimp.export(obj, filename, 'collada', pyassimp.postprocess.aiProcess_OptimizeMeshes)
        # self.save()
        # url = 'http://localhost:5001/encoded-joy-257818/us-central1/helloWorld'
        # data = self.conversion_geometries()
        # response = requests.post(url, data=data).text
        # print(type(response))
        # try:
        #     response = json.loads(response)
        # except JSONDecodeError:
        #     return
        # three_json = response.get('three_json')
        # self.three_json = three_json
        # self.derived_depth = response.get('derived_depth')
        # self.derived_height = response.get('derived_height')
        # self.derived_width = response.get('derived_width')
        self.save()

    def get_height(self):
        return float(self.height.lower) if self.height else None

    def get_width(self):
        return float(self.width.lower) if self.width else None

    def get_depth(self):
        return float(self.depth.lower) if self.depth else None

class Cabinets(ProductSubClass):
    pass


class Furniture(ProductSubClass):
    pass


class Lumber(ProductSubClass):
    pass


#     room_type = models.CharField(max_length=100, blank=True, null=True)
#     height = models.DecimalField(max_digits=5, decimal_places=2)
#     depth = models.DecimalField(max_digits=5, decimal_places=2)
#     width = models.DecimalField(max_digits=5, decimal_places=2)


# class Millwork(ProductSubClass):
#     pass



        # data = serialize_geometry(self)
        # url = 'http://localhost:5000/geoconverter/us-central1/helloWorld'


    # def serialize(self):
    #     main = self.serialize_remaining()
    #     main.update(self.serialize_size())
    #     main.update(self.serialize_applications())
    #     return main

    # def serialize_special(self):
    #     return {
    #         'details': self.serialize_remaining(),
    #         'size_and_shape': self.serialize_size(),
    #         'applications': self.serialize_applications(),
    #     }

    # def serialize_remaining(self):
    #     return {
    #         'label_color': self.label_color,
    #         'material': self.material,
    #         'sub_material': self.sub_material,
    #         'finish': self.finish,
    #         'surface_coating': self.surface_coating,
    #         'look': self.look,
    #         'shade_variation': self.shade_variation,
    #         'lrv': self.lrv,
    #         'cof': self.cof,
    #         'edge': self.edge,
    #         'end': self.end,
    #         'install_type': self.install_type,
    #         'sqft_per_carton': self.sqft_per_carton,
    #         'slip_resistant':self.slip_resistant
    #         }

    # def serialize_size(self):
    #     return {
    #         'thickness': self.thickness,
    #         'width': self.width.lower if self.width else None,
    #         'length': self.length.lower if self.length else None,
    #         'size': self.size,
    #         'square_inches': self.actual_size,
    #         'shape': self.shape
    #     }

    # def serialize_applications(self):
    #     return {
    #         'walls': self.walls,
    #         'countertops': self.countertops,
    #         'floors': self.floors,
    #         'cabinet_fronts': self.cabinet_fronts,
    #         'shower_floors': self.shower_floors,
    #         'shower_walls': self.shower_walls,
    #         'exterior_walls': self.exterior_walls,
    #         'exterior_floors': self.exterior_floors,
    #         'covered_walls': self.covered_walls,
    #         'covered_floors': self.covered_floors,
    #         'pool_linings': self.pool_linings,
    #         'bullnose': self.bullnose,
    #         'covebase': self.covebase,
    #         'corner_covebase': self.corner_covebase
    #         }

                # temp_file = io.StringIO(obj_content)
            # file = open(name, 'w')
            # file = file.write(obj_content)
            # file.close()
