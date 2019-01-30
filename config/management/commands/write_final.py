import decimal
import csv
import os
import glob
import sys
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from Products.models import (
    Finish,
    Image,
    Look,
    Edge,
    Material,
    Manufacturer,
    Product,
    ShadeVariation,
    SurfaceCoating,
    SubMaterial
    )

BASE_PATH = os.getcwd()


class Command(BaseCommand):

    def handle(self, *args, **options):
        current_line = 0
        line_total = None
        data_path = settings.DATA_PATH
        data_files = glob.glob(data_path)
        data = max(data_files, key=os.path.getctime)

        with open(data, 'r', newline='') as readfile:
            reader = csv.DictReader(readfile)
            headers = reader.fieldnames
            with open(settings.PRODUCTION_DATA_WRITE_PATH, 'w', newline='') as wf:
                writer = csv.DictWriter(wf, fieldnames=headers)
                writer.writeheader()
                for row in reader:
                    bbsku = row['bbsku']
                    product = Product.objects.filter(bb_sku=bbsku).first()
                    if not product:
                        continue
                    if not product.swatch_image:
                        continue
                    if not product.swatch_image.image:
                        continue
                    si_final = product.swatch_image.image.url

                    rs_final = None
                    try:
                        rs_final = product.room_scene.image.url
                    except:
                        pass

                    ti_final = None
                    try:
                        ti_final = product.tiling_image.image.url
                    except:
                        pass

                    row['image_local'] = si_final
                    row['image2_local'] = rs_final
                    row['tiling_image_local'] = ti_final
                    writer.writerow(row)


