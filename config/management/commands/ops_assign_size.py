from django.core.management.base import BaseCommand
from config.scripts.assign_size import assign_size
from SpecializedProducts.models import FinishSurface

class Command(BaseCommand):
    def handle(self, *args, **options):
        products = FinishSurface.objects.all()
        assign_size(products)
