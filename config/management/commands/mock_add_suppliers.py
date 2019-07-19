import datetime
import decimal
import random
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from config.scripts import lists
from Profiles.models import (
    BaseProfile,
    RetailerEmployeeProfile,
    ProEmployeeProfile,
)
from Groups.models import ServiceType, Company
from Addresses.models import Address, Zipcode
from UserProductCollections.models import RetailerLocation, ProProject
from UserProducts.models import RetailerProduct, ProjectProduct
from Products.models import Product
from .random_data.random_addresses import ADDRESSES
from .random_data.random_company_names import COMP_NAMES
from .random_data.random_names import RANDOM_NAMES

RETAILER = 'retailer'
PRO = 'pro'
SERVICE_TYPES = ('Architech', 'Contractor', 'Interior Designer', 'Carpenter', 'Engineer')


class Command(BaseCommand):

    @transaction.atomic()
    def handle(self, *args, **options):
        product_ids = Product.objects.all().values_list('pk', flat=True)
        random_names = RANDOM_NAMES
        random_addresses = ADDRESSES
        for comp_name in COMP_NAMES:
            user_model = get_user_model()
            password = '0gat_surfer'
            name = random.choice(random_names)
            del random_names[random_names.index(name)]
            email = name.replace(' ', '') + '@hotgmail.com'
            company_name = comp_name + '_demo_test'
            address = random.choice(random_addresses)
            del random_addresses[random_addresses.index(address)]
            company_type = random.choice((RETAILER, PRO))
            if company_type == RETAILER:
                user = user_model.objects.create_user(email=email, is_supplier=True, password=password)
            else:
                user = user_model.objects.create_user(email=email, is_pro=True, password=password)
            zipcode = Zipcode.objects.get(code=address['postalCode'])
            location_address = Address.objects.create(
                address_line_1=address['address1'],
                city=address.get('city', None),
                state=address['state'],
                postal_code=zipcode
            )
            service = random.choice(SERVICE_TYPES)
            service_object = ServiceType.objects.get_or_create(label=service)[0]
            company = Company.objects.create_company(
                user,
                name=company_name,
                phone_number='4044335741',
                email_verified=True,
                business_address=location_address,
                service=service_object
            )
            BaseProfile.objects.create_profile(
                user,
                company=company,
                owner=True,
                title='CEO'
                )
            addresses = [location_address]
            for x_ad in range(random.randint(0, 2)):
                new_add = random.choice(ADDRESSES)
                new_zip = Zipcode.objects.get(code=new_add['postalCode'])
                new_add_object = Address.objects.create(
                    address_line_1=new_add['address1'],
                    city=new_add.get('city', None),
                    state=new_add['state'],
                    postal_code=new_zip
                    )
                addresses.append(new_add_object)
                del ADDRESSES[ADDRESSES.index(new_add)]
            for addie in addresses:
                if user.is_supplier:
                    location = RetailerLocation.objects.create(
                        company=company,
                        address=addie,
                        phone_number='4044335741',
                        approved_online_seller=True,
                        approved_in_store_seller=True
                    )
                    max_count = product_ids.count()
                    rang_int = random.randint(10, max_count) // 5
                    location_prod_ids = list(product_ids)
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
                        sup_prod: RetailerProduct = RetailerProduct.objects.get_or_create(
                            product=product,
                            retailer=location,
                            )[0]
                        sup_prod.units_available_in_store = units_available
                        sup_prod.units_per_order = units_per_order
                        sup_prod.publish_in_store_price = True
                        sup_prod.in_store_ppu = price
                        sup_prod.lead_time_ts = datetime.timedelta(days=lead_time)
                        sup_prod.offer_installation = offer_install
                        sup_prod.save()
                else:
                    project = ProProject.objects.create(
                        owner=company,
                        address=addie
                        )
                    range_int = random.randint(10, 30)
                    project_prod_ids = list(product_ids)
                    for x in range(range_int):
                        prod_id = random.choice(project_prod_ids)
                        product = Product.objects.get(pk=prod_id)
                        del project_prod_ids[project_prod_ids.index(prod_id)]
                        ProjectProduct.objects.create(
                            project=project,
                            product=product
                        )
