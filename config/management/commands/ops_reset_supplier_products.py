from django.core.management.base import BaseCommand
from config.scripts.db_operations import reset_supplier_products

class Command(BaseCommand):

    def handle(self, *args, **options):
        reset_supplier_products()
