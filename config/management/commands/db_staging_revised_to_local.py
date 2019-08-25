from django.core.management.base import BaseCommand
from config.scripts.db_operations import staging_revised_to_local_revised

class Command(BaseCommand):
    def handle(self, *args, **options):
        staging_revised_to_local_revised()
