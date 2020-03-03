from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Suppliers.models import SupplierCompany
from Profiles.models import SupplierEmployeeProfile

class Command(BaseCommand):

    def handle(self, *args, **options):
        user_model = get_user_model()
        fake_comps = SupplierEmployeeProfile.objects.filter(user__demo=True).values_list('company__pk', flat=True).distinct()
        for comp in fake_comps:
            company = SupplierCompany.objects.get(pk=comp)
            company.delete()
        demos = user_model.objects.filter(demo=True)
        demos.delete()
