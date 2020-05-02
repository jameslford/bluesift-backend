from django.core.management.base import BaseCommand
from scripts.generate_data import refresh_all_demo_data
from config.models import ConfigTree
from Suppliers.models import SupplierProductTree


class Command(BaseCommand):
    def handle(self, *args, **options):
        refresh_all_demo_data()
        ConfigTree.refresh()
        for tree in SupplierProductTree.objects.all():
            tree.refresh()
