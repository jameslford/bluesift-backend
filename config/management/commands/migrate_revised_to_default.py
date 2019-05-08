from django.core.management.base import BaseCommand
from config.scripts.db_operations import revised_to_default

class Command(BaseCommand):
    def handle(self, *args, **options):
        revised_to_default()
