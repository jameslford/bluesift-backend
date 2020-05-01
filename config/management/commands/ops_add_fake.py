from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from Suppliers.models import SupplierCompany
from Profiles.models import SupplierEmployeeProfile
from scripts.addresses import add_zips


def delete_fake():
    user_model = get_user_model()
    fake_comps = (
        SupplierEmployeeProfile.objects.filter(user__demo=True)
        .values_list("company__pk", flat=True)
        .distinct()
    )
    for comp in fake_comps:
        company = SupplierCompany.objects.get(pk=comp)
        company.delete()
    demos = user_model.objects.filter(demo=True)
    demos.delete()


@transaction.atomic
def replace():
    delete_fake()
    # create_demo_users()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # add_zips()
        # create_addresses()
        replace()
        # add_additonal()
        # create_parent_tasks()
        # create_child_tasks()
