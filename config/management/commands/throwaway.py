from django.core.management.base import BaseCommand
from FinishSurfaces.models import FinishSurface

class Command(BaseCommand):

    def handle(self, *args, **options):
        fs_all = FinishSurface.objects.all()
        for item in fs_all:
            item.save()
