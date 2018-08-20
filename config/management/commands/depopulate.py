from django.core.management.base import BaseCommand, CommandError
from Products.models import Product, Manufacturer, Build, Look, Material


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        Manufacturer.objects.all().delete()
        Build.objects.all().delete()
        Look.objects.all().delete()
        Material.objects.all().delete()
        