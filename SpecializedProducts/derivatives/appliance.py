import io
import decimal
from django.db import models
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

    def convert_geometries(self):
        converter = ApplianceConverter(self)
        converter.convert()



class ApplianceConverter(Converter):

    def __init__(self, product):
        self.resolver = None
        super().__init__(product)

    def create_derived_obj(self):
        base_path = MediaStorage.base_path()
        return_path = self.get_3d_return_path()
        filename = 'derived_' + str(self.product.obj_file.name.split('/')[-1])
        print(filename)
        index = None
        data = self.product.obj_file.readlines()
        for num, line in enumerate(data):
            if 'mtllib'.encode('utf-8') in line:
                print(line)
                index = num
                break
        if not index:
            return self.product.obj_file
        path = base_path + return_path + filename
        data[index] = str(path).encode('utf-8')
        buffer = io.BytesIO()
        buffer.writelines(data)
        buffer.seek(0)
        self.resolver = WebResolver
        return buffer


    def get_initial(self) -> io.BytesIO:
        if not self.product.obj_file:
            return None
        if self.product.mtl_file:
            print(self.product.name, 'has mtlf')
            return self.create_derived_obj()
        res = self.download_bytes(self.product.obj_file.url)
        return res

    def convert(self):
        field: io.BytesIO = self.get_initial()
        if not field:
            return
        mes: trimesh.Trimesh = trimesh.load(field, 'obj', resolver=self.resolver)
        self.assign_sizes(mes)
        self.product.save_derived_glb(mes)

    def assign_sizes(self, mes: trimesh.Trimesh):
        conversion_unit = self.product.cm
        if conversion_unit != self.product.inches:
            mes.units = conversion_unit
            mes = mes.convert_units('inches')
        length, height, depth = mes.extents
        length = decimal.Decimal(round(length, 2))
        depth = decimal.Decimal(round(depth, 2))
        height = decimal.Decimal(round(depth, 2))
        self.product.derived_depth = depth
        self.product.derived_height = height
        self.product.derived_width = length



        # self.product.derived_depth

        # file = download_bytes(field.url)
        # print(file, field.url)
        # file.seek(0)
        # mes: trimesh.Trimesh = trimesh.load(file, 'obj', resolver=self.resolver)
        # blob = mes.export(None, 'glb')
        # name = str(self.product.bb_sku) + '.glb'
        # self.product.derived_gbl.save(name, ContentFile(blob), save=True)

            # print(line.decode('utf-8'))
        # fout = download_string(self.product.object.url)
        # with self.product.obj_file.open('r') as fin:
        #     data = fin.readlines()
        #     for num, line in enumerate(data):
        #         print(line)
        # for 
        # field: FieldFile = self.product.obj_file.open('rb')
        # with self.product.obj_file.open('r') as field:
        # self.product.derived_obj.save(filename, buffer, save=True)
        # print('line 100')
        # self.product.refresh_from_db()
        # return self.product.derived_obj
        # if self.product.derived_obj:
        #     file = download_bytes(self.product.derived_obj.url)
        #     return file
        # return self.product.obj_file
