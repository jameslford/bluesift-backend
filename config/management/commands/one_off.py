from django.core.management.base import BaseCommand
from scripts.suppliers import add_view_records


class Command(BaseCommand):
    def handle(self, *args, **options):
        add_view_records()
