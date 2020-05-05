from django.core.management.base import BaseCommand
from SpecializedProducts.models import Appliance


class Command(BaseCommand):
    def handle(self, *args, **options):
        for app in Appliance.objects.all():
            if not app.obj_file:
                app.delete()
                continue
            app.unit = "EACH"
            app.save()
