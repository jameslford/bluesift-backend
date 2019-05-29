from django.core.management.base import BaseCommand
from config.scripts.colors import assign_label_color

class Command(BaseCommand):
    def handle(self, *args, **options):
        assign_label_color()
