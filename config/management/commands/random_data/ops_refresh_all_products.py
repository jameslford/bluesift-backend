from django.core.management.base import BaseCommand
from config.scripts.db_operations import refresh_filters, revised_to_default
from config.scripts.operations import assign_size, assign_label_color, clean_products

class Command(BaseCommand):
    def handle(self, *args, **options):
        revised_to_default()
        clean_products()
        assign_size()
        assign_label_color()
        refresh_filters()
