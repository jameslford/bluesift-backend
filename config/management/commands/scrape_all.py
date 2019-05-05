from django.core.management.base import BaseCommand
from ...scripts.scrape import initialize_data, scrape_new
from ...scripts.images import get_images

class Command(BaseCommand):
    def handle(self, *args, **options):
        initialize_data()
        scrape_new()
        get_images()
