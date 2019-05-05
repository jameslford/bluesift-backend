from django.core.management.base import BaseCommand
from ...scripts.scraper_data import delete_data

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        confirm = input('Are you sure?? <type yes or no>')
        if confirm == 'yes':
            delete_data()
        return
