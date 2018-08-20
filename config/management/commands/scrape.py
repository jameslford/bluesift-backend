from django.core.management.base import BaseCommand, CommandError
from scraper import scrape_main

class Command(BaseCommand):
    def handle(self, *args, **options):
        scrape_main.run_all()
        