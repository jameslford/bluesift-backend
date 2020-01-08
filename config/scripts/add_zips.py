import os
import csv
from django.conf import settings
from Addresses.models import Zipcode, Coordinate

def add_zips():
    cwd = os.getcwd()
    if os.name == 'nt':
        path = f'{cwd}\\config\\management\\zips\\zipcodes.csv'
    else:
        path = f'{cwd}/config/management/zips/zipcodes.csv'
    # print(path)
    with open(path) as readfile:
        reader = csv.reader(readfile, delimiter=",")
        for row in reader:
            ziptry = Zipcode.objects.filter(code=row[0]).first()
            if ziptry:
                continue
            coord = Coordinate.objects.create(lat=float(row[1]), lng=float(row[2]))
            Zipcode.objects.get_or_create(code=row[0], centroid=coord)