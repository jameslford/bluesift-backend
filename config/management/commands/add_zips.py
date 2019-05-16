import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from Addresses.models import Zipcode, Coordinate


class Command(BaseCommand):

    def handle(self, *args, **options):
        path = settings.ZIP_PATH
        with open(path) as readfile:
            reader = csv.reader(readfile, delimiter=",")
            for row in reader:
                ziptry = Zipcode.objects.filter(code=row[0]).first()
                if ziptry:
                    continue
                coord = Coordinate.objects.create(lat=float(row[1]), lng=float(row[2]))
                Zipcode.objects.get_or_create(code=row[0], centroid=coord)
