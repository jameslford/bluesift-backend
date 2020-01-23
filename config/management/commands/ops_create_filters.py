from django.core.management.base import BaseCommand
from config.scripts.create_filters import create_finish_surface, create_appliance

class Command(BaseCommand):

    def handle(self, *args, **options):
        create_finish_surface()
        create_appliance()
