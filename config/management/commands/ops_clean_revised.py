from django.core.management.base import BaseCommand
from config.scripts.db_operations import run_scraper_cleaners, run_stock_clean

class Command(BaseCommand):

    def handle(self, *args, **options):
        run_stock_clean()
        run_scraper_cleaners()
