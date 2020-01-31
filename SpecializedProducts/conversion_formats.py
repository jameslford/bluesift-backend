import os
import requests
import io
import zipfile
from contextlib import closing
import boto3
from django.conf import settings
from django.core.files.base import ContentFile, File
from django.db.models.fields.files import FieldFile, FileField
from config.custom_storage import MediaStorage
# import PipAssimp
import trimesh
from trimesh.visual.resolvers import WebResolver
from Products.models import get_3d_return_path
from .models import ProductSubClass


SESSION = {'session': boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
}


def download_bytes(url: str):
    buffer = io.BytesIO()
    with requests.get(url, stream=True) as req:
        for chunk in req.iter_content(80111, True):
            if chunk:
                buffer.write(chunk)
    buffer.seek(0)
    req.close()
    return buffer


def download_string(url: str):
    buffer = io.StringIO()
    with requests.get(url, stream=True) as req:
        for chunk in req.iter_content(80111):
            if chunk:
                chunk.encode('utf-8')
                buffer.write(chunk)
    req.close()
    return buffer



# class ConversionFormat:

#     def __init__(self, product: ProductSubClass, extension: str, file_type=None):

#         ref, alt_ftype = product.map_extension(extension)
#         self.reference = ref
#         self.extension = extension
#         self.filetype = file_type if file_type else alt_ftype
#         self.filename = product.name + self.extension
        # self.reference.save(self.filename, ContentFile(''))


class ApplianceConverter:

    def __init__(self, product: ProductSubClass):

        self.product = product
        self.resolver = None

            # print(line.decode('utf-8'))
        # fout = download_string(self.product.object.url)
        # with self.product.obj_file.open('r') as fin:
        #     data = fin.readlines()
        #     for num, line in enumerate(data):
        #         print(line)
        # for 

    def create_derived_obj(self):
        base_path = MediaStorage.base_path()
        return_path = get_3d_return_path(self.product)

        filename = 'derived_' + str(self.product.obj_file.name.split('/')[-1])
        print(filename)
        # field: FieldFile = self.product.obj_file.open('rb')
        index = None
        # with self.product.obj_file.open('r') as field:
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
        # self.product.derived_obj.save(filename, buffer, save=True)
        # print('line 100')
        # self.product.refresh_from_db()
        buffer.seek(0)
        self.resolver = WebResolver
        return buffer
        # return self.product.derived_obj


    def get_initial(self) -> FileField:
        # if self.product.derived_obj:
        #     file = download_bytes(self.product.derived_obj.url)
        #     return file
        if not self.product.obj_file:
            return None
        if self.product.mtl_file:
            print(self.product.name, 'has mtlf')
            return self.create_derived_obj()
        res = download_bytes(self.product.obj_file.url)
        return res
        # return self.product.obj_file



    def convert(self):
        field: io.BytesIO = self.get_initial()
        if not field:
            return
        # file = download_bytes(field.url)
        # print(file, field.url)
        # file.seek(0)
        mes: trimesh.Trimesh = trimesh.load(field, 'obj', resolver=self.resolver)
        # mes: trimesh.Trimesh = trimesh.load(file, 'obj', resolver=self.resolver)
        blob: io.BytesIO = mes.export(None, 'glb')
        print(type(blob))
        name = str(self.product.bb_sku) + '.glb'
        self.product.derived_gbl.save(name, ContentFile(blob), save=True)


    def assign_sizes(self):
        pass


    # def get_file_object(self):

        #     buffer = io.StringIO()
        #     req = requests.get(self.initial_file.url)
        #     buffer.write(req.text)
        #     buffer.seek(0)
        #     print(buffer)
        #     print(req.elapsed)
        #     req.close()
        #     return buffer
        # with requests.get(self.initial_file.url, stream=True) as req:
        #     with io.BytesIO() as buffer:
        #         for chunk in req.iter_content(80111, True):
        #             if chunk:
        #                 buffer.write(chunk)
        # buffer.seek(0)
        # req.close()
        # return buffer

        # if not os.path.exists('temp'):
        #     os.mkdir('temp')

        # with requests.get(self.initial_file.url, stream=True) as r:
        #     with open(self.initial_local_filename, 'wb') as f:
        #         for chunk in r.iter_content(800111, True):
        #             if chunk:
        #                 f.write(chunk)
        # r.close()
        # f.close()
        # buffer = io.BytesIO()

        # print(r.elapsed)
        # obj = PipAssimp.load(self.initial_local_filename, 'obj')

        # for ftype in self.conversion_formats:
        #     PipAssimp.export(
        #         obj,
        #         'temp/' + ftype.filename,
        #         ftype.filetype,
        #         )
        #     temp_files = os.listdir('temp')
        #     for cwd_file in temp_files:
        #         if self.product.name in cwd_file:
        #             cwd_extension = '.' + cwd_file.split('.')[-1]
        #             reference = self.product.map_extension(cwd_extension)
        #             if not reference:
        #                 print(cwd_file + ' has invalid extension')
        #                 continue
        #             print(cwd_file + ' has valid extension')
        #             local_path = 'temp/' + cwd_file
        #             file = open(local_path, 'rb')
        #             ftype.reference.save(cwd_file, File(file), save=True)
        #             file.close()
        #             os.remove(local_path)
        #     os.remove(self.initial_local_filename)
        # PipAssimp.release(obj)
        # self.product.save()

