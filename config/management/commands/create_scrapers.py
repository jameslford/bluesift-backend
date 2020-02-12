from django.core.management.base import BaseCommand
from scripts.scrapers import create_scrapers

class Command(BaseCommand):

    def handle(self, *args, **options):
        create_scrapers()
