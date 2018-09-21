from django.core.management.base import BaseCommand, CommandError
from Products.models import Product


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Product.objects.all().delete()