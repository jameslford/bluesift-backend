import os
import csv
import random
import glob

from django.core.management.base import BaseCommand
from Products.models import Manufacturer, Category, Look, Material, Build, Product


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('extent')


    def handle(self, *args, **options):
        if not options:
            print('No argument specified for data sample: Random or Full')
            return
        data_path = "C:\\Users\\james\\Documents\\Code\\BuildingBook\\BBscraper\\downloaded_final\\*.csv"
        files = glob.glob(data_path)
        data = max(files, key=os.path.getctime)
        with open(data) as readfile:
            reader = csv.reader(readfile)
            if options['extent'] == 'Random':
                tiles = list(range(397,482))
                armstrong = random.sample(range(0,397), 100)
                fandm = random.sample(range(483, 5000), 200)
                sample = tiles + armstrong + fandm
                random_rows = [row for idx, row in enumerate(reader) if idx in sample]
                for row in random_rows:
                    bbsku = row[29]
                    product = None
                    if Product.objects.get(bb_sku=bbsku).exists():
                        print('wtf')
                        continue
                    else:
                        pass
