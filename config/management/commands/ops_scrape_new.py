from django.core.management.base import BaseCommand
from ...scripts.db_operations import initialize_data, scrape, scraper_to_revised
from ...scripts.images import get_images


class Command(BaseCommand):
    def handle(self, *args, **options):
        initialize_data()
        scrape()
        get_images()
        scraper_to_revised()
