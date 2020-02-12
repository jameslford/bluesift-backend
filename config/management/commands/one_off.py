from django.core.management.base import BaseCommand
from Scraper.models import ScraperGroup

class Command(BaseCommand):

    def handle(self, *args, **options):
        scraper: ScraperGroup = ScraperGroup.objects.get(manufacturer__label='crossville')
        scraper.scrape()
        # for scrap in scrapers:
        #     scrap.scrape()
