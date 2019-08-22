from django.core.management.base import BaseCommand
from ...scripts.db_operations import backup_db


class Command(BaseCommand):

    def handle(self, *args, **options):
        backup_db()
