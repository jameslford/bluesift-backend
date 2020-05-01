import decimal
from typing import List
import itertools
import random
import datetime
import requests
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from Accounts.models import User
from Addresses.models import Address
from Products.models import Product
from Profiles.models import (
    ConsumerProfile,
    SupplierEmployeeProfile,
    BaseProfile,
    LibraryProduct,
)
from Groups.models import SupplierCompany
from Suppliers.models import SupplierLocation, SupplierProduct
from Projects.models import Project, ProjectTask, ProjectProduct

PASSWORD = "0gat_surfer"


def random_date(deadline=None):
    if deadline:
        return deadline - datetime.timedelta(days=random.randint(1, 90))
    return timezone.now() + datetime.timedelta(days=random.randint(20, 40))


def __get_name_and_email():
    fake = Faker()
    name = fake.name()
    email = name.replace(" ", "")
    email = f"{email}@hotgmail.com"
    return [name, email]


def create_user(**kwargs):
    user_model: User = get_user_model()
    name, email = __get_name_and_email()
    is_supplier = kwargs.get("is_supplier", False)
    user = user_model.objects.filter(email=email).first()
    if user:
        return create_user(**kwargs)
    user = user_model.objects.create_user(
        email=email,
        password=PASSWORD,
        email_verified=True,
        is_active=True,
        demo=True,
        full_name=name,
        is_supplier=is_supplier,
    )
    return user


# @transaction.atomic
# def main():
#     address_groups = generate_address_groups()
#     for group in address_groups:
#         choice = random.randint(4, 6)
#         if choice > 4:
#             _generate_retailers(group)
#         else:
#             _generate_users(group)
