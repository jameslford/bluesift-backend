from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Profiles.models import CompanyAccount, SupplierProduct


class Command(BaseCommand):

    def handle(self, *args, **options):
        accounts = CompanyAccount.objects.filter(name__icontains='_test')
        for account in accounts:
            products = SupplierProduct.objects.filter(supplier__company_account=account)
            products.delete()
            account.delete()
        user_model = get_user_model()
        users = user_model.objects.filter(email__icontains='hotgmail')
        users.delete()
