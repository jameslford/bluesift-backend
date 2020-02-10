from django.core.management.base import BaseCommand
from scripts.assign_size import assign_size

class Command(BaseCommand):
    def handle(self, *args, **options):
        assign_size()
