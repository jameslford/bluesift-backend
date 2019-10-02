from django.core.management.base import BaseCommand
from ...scripts.mock_create import create_demo_users


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_demo_users()
