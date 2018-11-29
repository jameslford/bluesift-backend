from django.core.management.base import BaseCommand, CommandError
from Products.models import Product


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for prod in products:
            prod.set_prices()