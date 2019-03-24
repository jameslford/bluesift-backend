from django.core.management.base import BaseCommand
from Profiles.models import CompanyAccount
from django.contrib.auth import get_user_model


class Command(BaseCommand):

    def handle(self, *args, **options):
        accounts = CompanyAccount.objects.all()
        accounts.delete()
        user_model = get_user_model()
        users = user_model.objects.all()
        for user in users:
            if 'hotgmail' in user.email:
                user.auth_token.delete()
                user.delete()
