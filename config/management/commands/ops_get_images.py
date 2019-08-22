from django.core.management.base import BaseCommand
from ...scripts.images import get_images

class Command(BaseCommand):
    def handle(self, *args, **options):
        get_images()
