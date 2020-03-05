import io
import zipfile
import decimal
import tempfile
import requests
from django.db import models
from django.db import transaction
from django.contrib.postgres.fields import DecimalRangeField
import trimesh
from trimesh.visual.resolvers import WebResolver
from config.custom_storage import MediaStorage
from .base import Converter, ProductSubClass
# import base

class Appliance(ProductSubClass):
    inches = 'inches'
    cm = 'centimeter'
    mm = 'millimeter'
    ft = 'feet'
    unit_choices = [inches, cm, mm, ft]
    appliance_type = models.CharField(max_length=100, blank=True, null=True)
    # obj_unit = models.CharField(choices=choices, default=inches, max_length=60)
    room_type = models.CharField(max_length=100, null=True, blank=True)
    width = DecimalRangeField(null=True, blank=True)
    height = DecimalRangeField(null=True, blank=True)
    depth = DecimalRangeField(null=True, blank=True)


    def get_height(self):
        return float(self.height.lower) if self.height else None

    def get_width(self):
        return float(self.width.lower) if self.width else None

    def get_depth(self):
        return float(self.depth.lower) if self.depth else None

    def add_proprietary_files(self):
        converter = ApplianceConverter(self)
        converter.add_proprietary_files()

    def convert_geometries(self):
        converter = ApplianceConverter(self)
        converter.convert()

    def grouped_fields(self):
        return {
            'size_and_shaped': {
                'height': self.derived_height,
                'width': self.derived_width,
                'depth': self.derived_depth
                # 'size': self.size,
                # 'square_inches': self.actual_size,
                # 'shape': self.shape
                },
        }


class ApplianceConverter(Converter):

    def __init__(self, product):
        self.resolver = None
        super().__init__(product)

    def create_derived_obj(self):
        with self.product._obj_file.open('r') as data:
            buffer = io.StringIO()
            for line in data.readlines():
                line = line.decode()
                if 'mtllib' in line:
                    print(line)
                    new_line = 'mtllib ' + self.product._mtl_file.url
                    buffer.write(new_line)
                else:
                    buffer.write(line)
            buffer.seek(0)
            for line in buffer.readlines():
                if 'mtllib' in line:
                    print(line)
            buffer.seek(0)
            self.resolver = WebResolver
            return buffer


    def get_initial(self) -> io.BytesIO:
        if not self.product._obj_file:
            return None
        if self.product._mtl_file:
            print(self.product.name, 'has mtlf')
            return self.create_derived_obj()
        print(self.product.name, 'no mtl file')
        res = self.download_bytes(self.product._obj_file.url)
        return res


    def add_proprietary_files(self):
        product = self.product
        prop_array = [
            ['.rfa', product.rfa_file, product._rfa_file],
            ['_2d.dwg', product.dwg_2d_file, product._dwg_2d_file],
            ['_3d.dwg', product.dwg_3d_file, product._dwg_3d_file],
            ['.dxf', product.dxf_file, product._dxf_file]
            ]
        for ext, origin, destination in prop_array:
            print(ext, origin, destination)
            if not origin or origin == 'None':
                continue
            if destination:
                continue
            request = requests.get(origin, stream=True)
            # pylint: disable=no-member
            if request.status_code != requests.codes.ok:
                continue
            filename = str(product.pk) + ext
            lf = tempfile.NamedTemporaryFile()
            for block in request.iter_content(1024 * 8):
                if not block:
                    break
                lf.write(block)
            destination.save(filename, lf, save=True)


    def convert(self):
        if not self.product.obj_file:
            self.product.delete()
            return
        try:
            mes: trimesh.Trimesh = trimesh.load_remote(self.product.obj_file)
        except zipfile.BadZipFile:
            self.product.delete()
            return
        conversion_unit = self.product.cm
        if conversion_unit != self.product.inches:
            mes.units = conversion_unit
            mes = mes.convert_units('inches', True)
        self.assign_sizes(mes)
        self.product.save_derived_glb(mes)


    def assign_sizes(self, mes: trimesh.Trimesh):
        length, height, depth = mes.extents
        center = mes.centroid
        print(center.tolist(), type(center))
        length = decimal.Decimal(round(length, 2))
        depth = decimal.Decimal(round(depth, 2))
        height = decimal.Decimal(round(height, 2))
        self.product.derived_center = center.tolist()
        self.product.derived_depth = depth
        self.product.derived_height = height
        self.product.derived_width = length


class Range(Appliance):
    pass


class ColdStorage(Appliance):
    pass
