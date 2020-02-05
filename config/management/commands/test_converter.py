from django.core.management.base import BaseCommand
from SpecializedProducts.models import Appliance


class Command(BaseCommand):
    def handle(self, *args, **options):
        appliances = Appliance.objects.all()
        print(appliances.count())
        # appliances.delete()
        for appliance in appliances:
            appliance: Appliance = appliance
            print(appliance.name)
            appliance.convert_geometries()
            # if appliance._mtl_file:
            #     print(appliance.manufacturer_sku)