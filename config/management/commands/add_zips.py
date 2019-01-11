import csv


from django.conf import settings
from django.core.management.base import BaseCommand
from Addresses.models import Zipcode, Coordinate


class Command(BaseCommand):

    def handle(self, *args, **options):
        path = settings.ZIP_PATH
        # zip_dic = {}
        with open(path) as readfile:
            reader = csv.reader(readfile, delimiter=",")
            for row in reader:
                coord = Coordinate.objects.create(lat=float(row[1]), lng=float(row[2]))
                Zipcode.objects.get_or_create(code=row[0], centroid=coord)
                # zip_dic[row[0]] = [row[1], row[2]]
