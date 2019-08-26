from django.core.management.base import BaseCommand
# from config.scripts.revised import populate_db
from config.scripts.db_operations import staging_to_production

class Command(BaseCommand):
    def handle(self, *args, **options):
        print('method currently disabled for safety')
        # staging_to_production()
