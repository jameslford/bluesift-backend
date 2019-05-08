from django.core.management.base import BaseCommand
from config.scripts.db_operations import delete_scraper_default

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        confirm = input('Are you sure?? <type yes or no>')
        if confirm == 'yes':
            delete_scraper_default()
        return
