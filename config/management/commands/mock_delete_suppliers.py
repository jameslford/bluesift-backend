from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from Groups.models import Company

class Command(BaseCommand):

    @transaction.atomic()
    def handle(self, *args, **options):
        accounts = Company.objects.filter(name__icontains='_test')
        accounts.delete()
        user_model = get_user_model()
        users = user_model.objects.filter(email__icontains='hotgmail')
        users.delete()
