from django.core.management.base import BaseCommand
from Profiles.models import SupplierProduct


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        supp_prods = SupplierProduct.objects.all()
        for prod in supp_prods:
            prod.product.set_prices()