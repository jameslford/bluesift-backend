from django.core.management.base import BaseCommand
from config.models import ConfigTree

class Command(BaseCommand):

    def handle(self, *args, **options):
        trees = ConfigTree.objects.all()
        for tree in trees:
            tree.refresh()