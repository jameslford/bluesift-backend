import os
import requests
import boto3
from django.conf import settings
from django.core.files.base import ContentFile, File
import PipAssimp
from .models import ProductSubClass


SESSION = {'session': boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
}

class ConversionFormat:

    def __init__(self, product: ProductSubClass, extension: str, file_type=None):

        ref, alt_ftype = product.map_extension(extension)
        self.reference = ref 
        self.extension = extension
        self.filetype = file_type if file_type else alt_ftype
        self.filename = product.name + self.extension
        self.reference.save(self.filename, ContentFile(''))


class ApplianceConverter:

    def __init__(self, product: ProductSubClass):

        self.product = product
        self.upload_path = product.name + '/'
        self.initial_file = product.obj_file
        self.initial_local_filename = 'temp/' + self.initial_file.name.split('/')[-1]
        self.conversion_formats = [
            ConversionFormat(product, '.glb')
            ]

    def convert(self):
        if not os.path.exists('temp'):
            os.mkdir('temp')

        with requests.get(self.initial_file.url, stream=True) as r:
            with open(self.initial_local_filename, 'wb') as f:
                for chunk in r.iter_content(800111, True):
                    if chunk:
                        f.write(chunk)
        r.close()
        f.close()
        print(r.elapsed)
        obj = PipAssimp.load(self.initial_local_filename, 'obj')

        for ftype in self.conversion_formats:
            PipAssimp.export(
                obj,
                'temp/' + ftype.filename,
                ftype.filetype,
                )
            temp_files = os.listdir('temp')
            for cwd_file in temp_files:
                if self.product.name in cwd_file:
                    cwd_extension = '.' + cwd_file.split('.')[-1]
                    reference = self.product.map_extension(cwd_extension)
                    if not reference:
                        print(cwd_file + ' has invalid extension')
                        continue
                    print(cwd_file + ' has valid extension')
                    local_path = 'temp/' + cwd_file
                    file = open(local_path, 'rb')
                    ftype.reference.save(cwd_file, File(file), save=True)
                    file.close()
                    os.remove(local_path)
            os.remove(self.initial_local_filename)
        PipAssimp.release(obj)
        self.product.save()

