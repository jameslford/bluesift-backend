from django.core.management.base import BaseCommand, CommandError
from scraper import daltile_scraper

class Command(BaseCommand):
    daltile_scraper.run()