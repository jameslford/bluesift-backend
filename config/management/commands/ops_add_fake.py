from django.core.management.base import BaseCommand
from django.db import transaction
from scripts.demo_data import create_demo_users, add_additonal

class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        create_demo_users()
        add_additonal()
