from django.core.management.base import BaseCommand
from config.scripts.db_operations import migrate_all


class Command(BaseCommand):
    def handle(self, *args, **options):
        migrate_all()
