import requests
from faker import Faker
from Accounts.models import User
from django.contrib.auth import get_user_model

ADDRESS_URL = 'https://raw.githubusercontent.com/EthanRBrown/rrad/master/addresses-us-100.json'


def get_name_and_email():
    fake = Faker()
    name = fake.name()
    email = name.replace(' ', '')
    email = f'{email}@hotgamil.com'
    return [name, email]



def create_demo_users():
    user_count = 30
    retailer_count = 40
    pro_count = 40
    user_model = get_user_model()
    addresses_response = requests.get(ADDRESS_URL).json()
    addresses = addresses_response.get('addresses', [])
    for usernum in range(0, user_count):
        user_model = get_user_model()
        user: User = user_model()
        name, email = get_name_and_email()
        user.full_name = name
        user.emai = email







