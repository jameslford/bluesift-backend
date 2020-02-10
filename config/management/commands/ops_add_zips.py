from django.core.management.base import BaseCommand
from scripts.add_zips import add_zips


class Command(BaseCommand):
    def handle(self, *args, **options):
        add_zips()

