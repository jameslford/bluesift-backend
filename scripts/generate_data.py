# from .demo_data import
import random
from django.contrib.auth import get_user_model
from django.db import transaction
from Profiles.models import SupplierEmployeeProfile, ConsumerProfile
from Suppliers.models import SupplierCompany
from Addresses.models import Address
from Projects.models import Project
from scripts.addresses import create_addresses, generate_address_groups
from scripts.suppliers import generate_retailers, refresh_supplier_products
from scripts.projects import (
    generate_users,
    create_parent_tasks,
    create_child_tasks,
    add_group_products,
    add_task_products,
)


def delete_fake():
    user_model = get_user_model()
    fake_comps = (
        SupplierEmployeeProfile.objects.filter(user__demo=True)
        .values_list("company__pk", flat=True)
        .distinct()
    )
    SupplierCompany.objects.filter(pk__in=fake_comps).delete()
    demos = user_model.objects.filter(demo=True)
    for demo in demos:
        cons_profile = ConsumerProfile.objects.filter(user=demo).first()
        if cons_profile:
            Project.objects.filter(owner=demo.profile).delete()
        demo.delete()


@transaction.atomic
def refresh_all_demo_data():
    delete_fake()
    if Address.objects.all().count() < 150:
        create_addresses()
    address_groups = generate_address_groups()
    for group in address_groups:
        choice = random.randint(4, 6)
        if choice > 4:
            generate_retailers(group)
        else:
            generate_users(group)
    refresh_supplier_products()
    add_group_products()
    create_parent_tasks()
    create_child_tasks()
    add_task_products()
