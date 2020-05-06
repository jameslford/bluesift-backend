from django.core.management.base import BaseCommand
from django.db import transaction
from scripts.finish_surfaces import assign_tiling_image


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        assign_tiling_image()
