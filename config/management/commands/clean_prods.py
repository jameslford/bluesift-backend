from django.core.management.base import BaseCommand
from Products.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        products = Product.objects.filter(swatch_image__image=None)
        products.delete()
