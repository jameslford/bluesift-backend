from django.core.management.base import BaseCommand
from scripts.projects import add_group_products, add_task_products


class Command(BaseCommand):
    def handle(self, *args, **options):
        add_group_products()
        add_task_products()
