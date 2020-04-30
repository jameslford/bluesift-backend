from django.core.management.base import BaseCommand
from Products.models import Product
from Projects.models import Project


class Command(BaseCommand):
    def handle(self, *args, **options):
        prods = Product.subclasses.all().select_subclasses()
        for prod in prods:
            prod.save()
        for proj in Project.objects.all():
            proj.save()
