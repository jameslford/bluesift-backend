from django.core.management.base import BaseCommand
from scripts.db_operations import rename

class Command(BaseCommand):
    def handle(self, *args, **options):
        rename()