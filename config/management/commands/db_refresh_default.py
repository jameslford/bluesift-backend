from django.core.management.base import BaseCommand
from config.scripts.db_operations import refresh_default_database

class Command(BaseCommand):
    def handle(self, *args, **options):
        refresh_default_database()
