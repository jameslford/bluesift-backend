from django.core.management.base import BaseCommand
from .process_image_script import process_images, process_color


class Command(BaseCommand):

    def handle(self, *args, **options):
        process_images()
        process_color()
