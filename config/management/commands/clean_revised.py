from django.core.management.base import BaseCommand
from config.scripts.db_operations import clean_revised

class Command(BaseCommand):

    def handle(self, *args, **options):
        clean_revised()