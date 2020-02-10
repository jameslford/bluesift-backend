from django.core.management.base import BaseCommand
from scripts.mock_create import create_demo_users
from scripts.mock_create_additional import add_additonal

class Command(BaseCommand):

    def handle(self, *args, **options):
        create_demo_users()
        add_additonal()
