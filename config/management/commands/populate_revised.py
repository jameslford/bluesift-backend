from django.core.management.base import BaseCommand
from config.scripts.revised import populate_db

class Command(BaseCommand):
    def handle(self, *args, **options):
        populate_db()
