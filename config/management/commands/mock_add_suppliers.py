import datetime
import decimal
import random
from django.db import transaction
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from config.scripts import lists
from Profiles.models import (
    CompanyAccount,
    CompanyShippingLocation,
    EmployeeProfile,
    SupplierProduct
)
from Addresses.models import Address, Zipcode
from Products.models import Product


class Command(BaseCommand):

    @transaction.atomic()
    def handle(self, *args, **options):
        product_ids = Product.objects.all().values_list('pk', flat=True)
        for email, address, comp_name in zip(lists.emails, lists.addresses, lists.company_names):
            print(email, address, comp_name)
            user_model = get_user_model()
            password = 'tomatoes'
            user = user_model.objects.create_user(email=email, is_supplier=True, password=password)
            zipcode = Zipcode.objects.get(code=address[3])
            location_address = Address.objects.create(
                address_line_1=address[0],
                city=address[1],
                state=address[2],
                postal_code=zipcode
            )
            company = CompanyAccount.objects.create(
                name=comp_name,
                phone_number=lists.phone_number,
                email_verified=True
            )
            EmployeeProfile.objects.create(
                user=user,
                company_account=company,
                company_account_owner=True,
                title='Mr. CEO'
            )
            location = CompanyShippingLocation.objects.create(
                company_account=company,
                address=location_address,
                phone_number=lists.phone_number,
                approved_online_seller=True,
                approved_in_store_seller=True
            )
            max_count = product_ids.count()
            rang_int = random.randint(10, max_count) // 5
            location_prod_ids = list(product_ids)
            print(location_prod_ids)
            for x in range(rang_int):
                price = random.uniform(1, 10)
                price = round(float(price), 2)
                price = decimal.Decimal(price)
                units_available = random.randint(10, 60)
                units_per_order = decimal.Decimal(3.5)
                select_id = random.choice(location_prod_ids)
                del location_prod_ids[location_prod_ids.index(select_id)]
                product = Product.objects.get(pk=select_id)
                lead_time = random.randint(1, 14)
                offer_install = random.choice([True, False])
                sup_prod = SupplierProduct.objects.get_or_create(
                    product=product,
                    supplier=location,
                    )[0]
                sup_prod.units_available_in_store = units_available
                sup_prod.units_per_order = units_per_order
                sup_prod.priced_in_store = True
                sup_prod.in_store_ppu = price
                sup_prod.lead_time_ts = datetime.timedelta(days=lead_time)
                sup_prod.offer_installation = offer_install
                sup_prod.save()
