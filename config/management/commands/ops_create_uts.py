
from django.core.management.base import BaseCommand
from scripts.create_usertypes import create_usertypes



class Command(BaseCommand):
    def handle(self, *args, **options):
        create_usertypes()
