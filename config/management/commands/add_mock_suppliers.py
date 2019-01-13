from django.core.management.base import BaseCommand
from config.management.commands import lists
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from Profiles.models import CompanyAccount, CompanyShippingLocation
from Addresses.models import Address, Zipcode


class Command(BaseCommand):

    def handle(self, *args, **options):
        CompanyAccount.objects.all().delete()
        CompanyShippingLocation.objects.all().delete()
        for q in lists.users:
            loc_dict = lists.create_user_data(q)
            user_model = get_user_model()
            user, created = user_model.objects.get_or_create(email=loc_dict['email'])
            # if created:
            password = loc_dict['password']
            password = make_password(password)
            user.password = password
            user.is_supplier = True
            user.is_active = True
            user.save()
            Token.objects.create(user=user)
            account, created = CompanyAccount.objects.get_or_create(account_owner=user, name=loc_dict['ca_name'])
            for location in loc_dict['locations']:
                nickname = location['nickname']
                number = location['number']
                street = location['address_line']
                city = location['city']
                state = location['state']
                zip_code = location['zip']
                zip_code = Zipcode.objects.get(code=zip_code)
                address, created = Address.objects.get_or_create(
                    address_line_1=street,
                    city=city,
                    state=state,
                    postal_code=zip_code,
                )
                new_loc, created = CompanyShippingLocation.objects.get_or_create(
                    company_account=account,
                    nickname=nickname,
                    approved_in_store_seller=True,
                    approved_online_seller=True,
                    phone_number=number
                )

            