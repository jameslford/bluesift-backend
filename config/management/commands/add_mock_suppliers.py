import datetime
import decimal
import random
from django.core.management.base import BaseCommand
# from rest_framework.authtoken.models import Token
# from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from config.management.commands import lists
from Profiles.models import (
    CompanyAccount,
    CompanyShippingLocation,
    EmployeeProfile,
    SupplierProduct
)
from Addresses.models import Address, Zipcode
from Products.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        product_ids = Product.objects.all().values_list('id', flat=True)
        for email, address, comp_name in zip(lists.emails, lists.addresses, lists.company_names):
            user_model = get_user_model()
            # password = make_password('tomatoes')
            password = 'tomatoes'
            user = user_model.objects.create_user(email=email, is_supplier=True, password=password)
            # Token.objects.create(user=user)
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
            rang_int = random.randint(10, max_count)
            location_prod_ids = list(product_ids)
            for x in range(rang_int):
                price = random.uniform(1, 10)
                price = round(float(price), 2)
                price = decimal.Decimal(price)
                units_available = random.randint(10, 60)
                units_per_order = decimal.Decimal(3.5)
                select_id = random.choice(location_prod_ids)
                location_prod_ids.remove(select_id)
                product = Product.objects.get(pk=select_id)
                # available_online = random.choice([True, False])
                lead_time = random.randint(1, 14)
                offer_install = random.choice([True, False])
                SupplierProduct.objects.create(
                    product=product,
                    supplier=location,
                    units_available_in_store=units_available,
                    units_per_order=units_per_order,
                    for_sale_in_store=True,
                    in_store_ppu=price,
                    # for_sale_online=available_online,
                    lead_time_ts=datetime.timedelta(days=lead_time),
                    offer_installation=offer_install
                )


    #     CompanyAccount.objects.all().delete()
    #     CompanyShippingLocation.objects.all().delete()
    #     for q in lists.users:
    #         loc_dict = lists.create_user_data(q)
    #         user_model = get_user_model()
    #         user, created = user_model.objects.get_or_create(email=loc_dict['email'])
    #         # if created:
    #         password = loc_dict['password']
    #         password = make_password(password)
    #         user.password = password
    #         user.is_supplier = True
    #         user.is_active = True
    #         user.save()
    #         Token.objects.create(user=user)
    #         account, created = CompanyAccount.objects.get_or_create(account_owner=user, name=loc_dict['ca_name'])
    #         for location in loc_dict['locations']:
    #             nickname = location['nickname']
    #             number = location['number']
    #             street = location['address_line']
    #             city = location['city']
    #             state = location['state']
    #             zip_code = location['zip']
    #             zip_code = Zipcode.objects.get(code=zip_code)
    #             address, created = Address.objects.get_or_create(
    #                 address_line_1=street,
    #                 city=city,
    #                 state=state,
    #                 postal_code=zip_code,
    #             )
    #             new_loc, created = CompanyShippingLocation.objects.get_or_create(
    #                 company_account=account,
    #                 nickname=nickname,
    #                 approved_in_store_seller=True,
    #                 approved_online_seller=True,
    #                 phone_number=number
    #             )
