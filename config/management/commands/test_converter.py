from django.core.management.base import BaseCommand
from Products.models import Product
from SpecializedProducts.models import FinishSurface, Appliance


class Command(BaseCommand):
    def handle(self, *args, **options):
        # products = Product.subclasses.all().select_subclasses()
        apps = Appliance.objects.all()
        fins = FinishSurface.objects.all()
        for prod in apps:
            prod.convert_geometries()
        for fin in fins:
            fin.convert_geometries()
