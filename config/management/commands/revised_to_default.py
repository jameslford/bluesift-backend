from django.core.management.base import BaseCommand
from config.scripts.revised import add_to_default

class Command(BaseCommand):
    def handle(self, *args, **options):
        add_to_default()