import trimesh
from django.core.management.base import BaseCommand
from Products.models import Product
from SpecializedProducts.models import FinishSurface, Appliance
from SpecializedProducts.conversion_formats import ApplianceConverter, ConversionFormat


class Command(BaseCommand):
    def handle(self, *args, **options):
        # initial_filename = 'temp/TVDR4804FBX_obj.obj'
        # paths = ['temp/TVDR4804FBX_obj.glb']
        # mes: trimesh.Trimesh = trimesh.load(initial_filename)
        # for path in paths:
        #     mes.export(path, 'glb')
        # products = Product.subclasses.all().select_subclasses()
        # apps = Appliance.objects.filter(pk='8bb459c6-aa2a-4b86-aacb-b7e3c575c0d1')
        # apps = Appliance.objects.filter(geometry_clean=False)
        apps = Appliance.objects.all()
        for prod in apps:
            conv = ApplianceConverter(prod)
            conv.convert()
            # prod.convert_geometries()
        # fins = FinishSurface.objects.all()
        # for fin in fins:
        #     fin.convert_geometries()
# 48"W. Tuscany Range - TVDR480