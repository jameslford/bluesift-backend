from django.core.management.base import BaseCommand
from config.scripts.db_operations import load_from_backup
from Scraper.models import ScraperSubgroup

class Command(BaseCommand):

    def handle(self, *args, **options):
        revised_count = ScraperSubgroup.objects.all().count()
        default_count = ScraperSubgroup.objects.using('scraper_default').all().count()
        if revised_count > 0 or default_count > 0:
            self.stdout.write('Data already in database. Will need to flush')
            return
        load_from_backup()