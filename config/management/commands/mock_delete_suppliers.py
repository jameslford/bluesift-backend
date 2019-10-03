from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from Groups.models import Company


class Command(BaseCommand):

    @transaction.atomic()
    def handle(self, *args, **options):
        user_model = get_user_model()
        users = user_model.objects.filter(demo=True)
        accounts = None
        if settings.ENVIRONMENT != 'local':
            accounts = Company.objects.all()
        else:
            accounts = Company.objects.filter(name__icontains='demo')
        accounts.delete()
        users.delete()
        # users = user_model.objects.filter(email__icontains='hotgmail')
