from django.core.management.base import BaseCommand
from utils.images import remove_background
from Products.models import Product

class Command(BaseCommand):

    def handle(self, *args, **options):
        # products = Product.subclasses.all().select_subclasses()
        products = Product.subclasses.filter().select_subclasses()
        print(products.query)
        # remove_background()



