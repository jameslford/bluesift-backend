from django.core.management.base import BaseCommand, CommandError
from Products.models import Product, ProductType, Manufacturer, Application


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        ProductType.objects.all().delete()
        Manufacturer.objects.all().delete()
        Application.objects.all().delete()