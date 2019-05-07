from django.core.management.base import BaseCommand
# from config.scripts.revised import populate_db
from config.scripts.upload_data import upload_to_production

class Command(BaseCommand):
    def handle(self, *args, **options):
        upload_to_production()
