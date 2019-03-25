import csv
import os
import glob
import sys
from django.conf import settings
from .add_product import add_product
from django.core.management.base import BaseCommand
from .add_finish_surface import add_finish_surface
from .process_image_script import process_images

BASE_PATH = os.getcwd()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--update', action='store_true', help='Update exististing products with new data')

    def handle(self, *args, **options):
        current_line = 0
        line_total = None
        data_path = settings.DATA_PATH
        data_files = glob.glob(data_path)
        update = options['update']
        data = max(data_files, key=os.path.getctime)

        with open(data) as f:
            line_total = sum(1 for rq in f)
            f.close()

        with open(data, 'r', newline='') as readfile:
            reader = csv.DictReader(readfile)
            for row in reader:
                # print(row['name'], current_line)
                product = add_product(row, update)
                if not product:
                    # print('no prod')
                    continue
                # product = product.save()
                finish_surface = add_finish_surface(row)
                if not finish_surface:
                    # print('no fs')
                    # product.delete()
                    continue
                product.content = finish_surface
                product.save()

                current_line += 1
                percentage_complete = round((current_line/line_total) * 100, 3)
                percentage_complete = str(percentage_complete) + '%'
                sys.stdout.write('\r')
                sys.stdout.write(percentage_complete)
                sys.stdout.flush()

        process_images()
