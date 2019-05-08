from django.core.management.base import BaseCommand
from config.scripts.db_operations import scraper_to_revised

class Command(BaseCommand):
    def handle(self, *args, **options):
        scraper_to_revised()
