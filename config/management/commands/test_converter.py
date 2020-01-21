import random
from django.core.management.base import BaseCommand
from SpecializedProducts.models import FinishSurface


class Command(BaseCommand):
    def handle(self, *args, **options):
        one = FinishSurface.objects.all().first()
        one.convert_objects()