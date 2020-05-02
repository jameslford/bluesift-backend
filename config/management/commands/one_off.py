from django.core.management.base import BaseCommand
from scripts.demo_data import choose_image
from config.models import ConfigTree
from Suppliers.models import SupplierProductTree
from scripts.projects import add_task_products


class Command(BaseCommand):
    def handle(self, *args, **options):
        add_task_products()
        # ConfigTree.refresh()
        # for tree in SupplierProductTree.objects.all():
        #     tree.refresh()

        # pass
        # prods = Product.subclasses.all().select_subclasses()
        # for prod in prods:
        #     prod.save()
        # for proj in Project.objects.all():
        #     proj.save()
