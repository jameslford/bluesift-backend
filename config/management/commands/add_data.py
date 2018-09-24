import decimal
import csv
import os
import random
import glob

from django.conf import settings
from django.core.management.base import BaseCommand
from Products.models import Manufacturer, Category, Look, Material, Build, Product, Finish, Image


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('extent')


    def handle(self, *args, **options):
        if not options:
            print('No argument specified for data sample: Random or Full')
            return
        data_path = settings.DATA_PATH
        files = glob.glob(data_path)
        data = max(files, key=os.path.getctime)
        with open(data) as readfile:
            reader = csv.reader(readfile)
            if options['extent'] == 'Random':
                tiles = list(range(397, 482))
                armstrong = random.sample(range(0, 397), 100)
                fandm = random.sample(range(483, 5000), 200)
                sample = tiles + armstrong + fandm
                random_rows = [row for idx, row in enumerate(reader) if idx in sample]
                for row in random_rows:
                    bbsku = row[29]
                    if Product.objects.filter(bb_sku=bbsku).exists():
                        continue
                    else:
                        image_actual = row[0]
                        manufacturer_name = row[2]
                        build_label = row[7]
                        material_label = row[9]
                        original_image = row[6]
                        category = row[31]
                        look_label = row[13]
                        finish_label = row[14]

                        category = Category.objects.get_or_create(label=category)[0]
                        manufacturer = Manufacturer.objects.get_or_create(name=manufacturer_name)[0]
                        build = Build.objects.get_or_create(label=build_label, category=category)[0]
                        image = Image.objects.get_or_create(original_url=original_image, image=original_image)[0]
                        # date_scraped = row[28]


                        material = None
                        if material_label:
                            material = Material.objects.get_or_create(label=material_label, category=category)[0]

                        look = None
                        if look_label:
                            look = Look.objects.get_or_create(label=look_label)[0]

                        finish = None
                        if finish_label:
                            finish = Finish.objects.get_or_create(label=finish_label)[0]
                        
                        thickness = None
                        try:
                            thickness = decimal.Decimal(row[8])
                        except:
                            thickness = 0
                        # cof = None

                        # # lrv = row[15]
                        # residential_warranty = row[17]
                        # commercial_warranty = row[18]
                        # for cat in [residential_warranty, commercial_warranty]:
                        #     try:
                        #         cat = int(cat)
                        #     else:
                        #         cat = None




                        arguments = {
                            'name': row[1],
                            'bb_sku': bbsku,
                            'manufacturer_url': row[3],
                            'manufacturer_color': row[4],
                            'manu_collection': row[5],
                            'thickness':  thickness,
                            'manufacturer_sku': row[10],
                            'length': row[11],
                            'width': row[12],
                            # 'residential_warranty': row[17], 
                            # 'lrv': row[15],
                            # 'cof': row[16],
                            # 'commercial_warranty': row[18],
                            'walls': row[19],
                            'countertops': row[20],
                            'floors': row[21],
                            'cabinet_fronts': row[22],
                            'shower_floors': row[23],
                            'shower_walls': row[24],
                            'exterior': row[25],
                            'covered': row[26],
                            'pool_linings': row[27],
                            'look': look,
                            'finish': finish,
                            'notes': row[30],
                            'manufacturer': manufacturer,
                            'build': build,
                            'material': material,
                            'image': image,
                        }

                        kwargs = {k: v for k, v in arguments.items() if v is not None or v != ''}

                        Product.objects.create(**kwargs)
    



                            # name=name,
                            # bb_sku=bbsku,
                            # manufacturer=manufacturer,
                            # manufacturer_url=url,
                            # image=image,
                            # build=build,
                            # material=material,
                            # walls=walls,
                            # countertops=countertops,
                            # floors=floors,
                            # cabinet_fronts=cabinet_fronts,
                            # shower_floors=shower_floors,
                            # shower_walls=shower_walls,
                            # exterior=exterior,
                            # covered=covered,
                            # pool_linings=pool_lining,
                            # thickness=thickness,
                            # manufacturer_sku=manufacturer_sku,
                            # manu_collection=manufacturer_collection,
                            # residential_warranty=residential_warranty,
                            # commercial_warranty=commercial_warranty,
                            # lrv=lrv,
                            # cof=cof,
                            # manufacturer_color=manufacturer_color,
                            # width=width,
                            # length=length,
                            # look=look,
                            # finish=finish,
                            # # notes=notes