import decimal
import csv
import requests
import os
import random
import glob
import io
from django.conf import settings

# from io import BytesIO
from django.core.files import File
# from django.core import files
# from django.core.files.temp import NamedTemporaryFile
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
    SurfaceTexture,
    SubMaterial
    )

BASE_PATH = os.getcwd()

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('update')


    def handle(self, *args, **options):
        data_path = settings.DATA_PATH
        data_files = glob.glob(data_path)
        data = max(data_files, key=os.path.getctime)
        with open(data, 'r', newline='') as readfile:
            reader = csv.DictReader(readfile)
            for row in reader:
                bbsku = row['bbsku']
                product, created = Product.objects.get_or_create(bb_sku=bbsku)
                if not created and options['update'] == 'add':
                    continue
                name = row['name']
                image_original = row['image_original']
                image_local = row['image_local']
                # image_final = row['image_final']
                image2_original = row['image2_original']
                image2_local = row['image2_local']
                # image2_final = row['image2_final']
                tiling_image = row['tiling_image']
                tiling_image_local = row['tiling_image_local']
                # tiling_image_final = row['tiling_image_final']

                manufacturer_name = row['manufacturer_name']
                manufacturer_url = row['manufacturer_url']
                manufacturer_collection = row['manufacturer_collection']
                manufacturer_color = row['manufacturer_color']
                manufacturer_sku = row['manufacturer_sku']

                material_label = row['material_label']
                sub_material_label = row['sub_material_label']
                look_label = row['look_label']
                finish_label = row['finish_label']
                gloss_level = row['gloss_level']
                texture_label = row['texture_label']

                # form_label = row['form_label']
                thickness = row['thickness']
                try:
                    thickness = decimal.Decimal(thickness)
                except:
                    thickness = None
                length = row['length']
                width = row['width']

                lrv = row['lrv']
                cof = row['cof']
                wet_cof = row['wet_cof']

                generic_color = row['generic_color']
                shade = row['shade']
                shade_variation = row['shade_variation']

                edge = row['edge']
                end = row['end']

                rating_value = row['rating_value']
                rating_count = row['rating_count']

                commercial = row['commercial']
                residential_warranty = row['residential_warranty']
                commercial_warranty = row['commercial_warranty']
                light_commercial_warranty = row['light_commercial_warranty']

                install_type = row['install_type']
                sqft_per_carton = row['sqft_per_carton']
                weight_per_carton = row['weight_per_carton']
                recommended_grout = row['recommended_grout']
                notes = row['notes']

                slip_resistance = row['slip_resistance']

                walls = row['walls']
                countertops = row['countertops']
                floors = row['floors']
                cabinet_fronts = row['cabinet_fronts']
                shower_floors = row['shower_floors']
                shower_walls = row['shower_walls']
                exterior_walls = row['exterior_walls']
                exterior_floors = row['exterior_floors']
                covered_walls = row['covered_walls']
                covered_floors = row['covered_floors']
                pool_lining = row['pool_lining']

                manufacturer = Manufacturer.objects.get_or_create(label=manufacturer_name)[0]

                if not material_label:
                    print(name)
                    continue
                material = Material.objects.get_or_create(label=material_label)[0]
                product.material = material
                product.name = name
                product.manufacturer = manufacturer
                product.manufacturer_url = manufacturer_url
                product.manufacturer_sku = manufacturer_sku
                product.manu_collection = manufacturer_collection
                product.manufacturer_color = manufacturer_color
                product.slip_resistant = slip_resistance
                product.residential_warranty = residential_warranty
                product.commercial_warranty = commercial_warranty
                product.light_commercial_warranty = light_commercial_warranty
                product.install_type = install_type
                product.commercial = commercial
                product.sqft_per_carton = sqft_per_carton
                product.lrv = lrv
                product.cof = cof
                product.notes = notes
                product.shade = shade
                product.actual_color = generic_color

                if edge:
                    edge_obj = Edge.objects.get_or_create(label=edge)[0]
                    product.edge = edge_obj
                if shade_variation:
                    shadvar = ShadeVariation.objects.get_or_create(label=shade_variation)[0]
                    product.shade_variation = shadvar
                if look_label:
                    look = Look.objects.get_or_create(label=look_label)[0]
                    product.look = look
                if sub_material_label:
                    sub_material = SubMaterial.objects.get_or_create(label=sub_material_label, material=material)[0]
                    product.sub_material = sub_material
                if finish_label:
                    surface_coating = SurfaceCoating.objects.get_or_create(label=finish_label, material=material)[0]
                    product.surface_coating = surface_coating
                if texture_label or gloss_level:
                    finish_holder = None
                    if texture_label:
                        finish_holder = texture_label
                    if gloss_level:
                        finish_holder = gloss_level
                    finish = Finish.objects.get_or_create(label=finish_holder, material=material)[0]
                    product.finish = finish
                swatch_image = Image.objects.get_or_create(original_url=image_original)[0]
                if not swatch_image.image:
                    read_image = image_local.strip('"')
                    with open(read_image, 'rb') as f:
                        # image_file = File(f)
                        image_name = f.name.split('/')[-1]
                        swatch_image.image.save(image_name, f)
                        swatch_image.save()
                        product.swatch_image = swatch_image
                        f.close()
                if image2_original:
                    room_scene = Image.objects.get_or_create(original_url=image2_original)[0]
                    if not room_scene.image:
                        with open(image2_local, 'rb') as f2:
                            image_file2 = File(f2)
                            room_scene.image = image_file2
                            room_scene.save()
                            product.room_scene = room_scene
                            f2.close()
                if tiling_image:
                    tiling = Image.objects.get_or_create(original_url=tiling_image)[0]
                    if not tiling.image:
                        with open(tiling_image_local, 'rb') as f3:
                            tiling_file = File(f3)
                            tiling.image = tiling_file
                            tiling.save()
                            product.tiling_image = tiling
                            f3.close()
                product.thickness = thickness
                product.length = length
                product.width = width

                product.walls = walls
                product.floors = floors
                product.countertops = countertops
                product.cabinet_fronts = cabinet_fronts
                product.shower_floors = shower_floors
                product.shower_walls = shower_walls
                product.exterior_walls = exterior_walls
                product.exterior_floors = exterior_floors
                product.covered_walls = covered_walls
                product.covered_floors = covered_floors
                product.pool_linings = pool_lining
                product.save()



        '''if not options:
            print('No argument specified for data sample: Random or Full')
            return
        data_path = settings.DATA_PATH
        data_files = glob.glob(data_path)
        data = max(data_files, key=os.path.getctime)
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
                        # image_request = requests.get(original_image)
                        # if image_request.status_code == requests.codes.ok:
                        #     # temp_img = NamedTemporaryFile(delete=True)
                        #     # temp_img.write(image_request.content)
                        #     # temp_img.flush()
                        #     fp = BytesIO()
                        #     fp.write(image_request.content)
                        #     image_name = image_actual.split('\\')[-1]
                        #     image_file = files.File(fp)
                        image = Image.objects.get_or_create(original_url=original_image)[0]





                        category = Category.objects.get_or_create(label=category)[0]
                        manufacturer = Manufacturer.objects.get_or_create(label=manufacturer_name)[0]
                        build = Build.objects.get_or_create(label=build_label, category=category)[0]
                        requests.encoding = 'utf-8'
                        # image = Image.objects.get_or_create(original_url=original_image, image=image_request)[0]
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
                        # # notes=notes '''