import random
import datetime
import requests
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from Accounts.models import User
from Addresses.models import Address
from Products.models import Product
from Profiles.models import ConsumerProfile, RetailerEmployeeProfile, ProEmployeeProfile, BaseProfile
from Groups.models import ServiceType, ProCompany, RetailerCompany, BaseGroup
from Retailers.models import RetailerLocation
from Projects.models import Project

ADDRESS_URL = 'https://raw.githubusercontent.com/EthanRBrown/rrad/master/addresses-us-all.min.json'
PASSWORD = '0gat_surfer'
SERVICE_TYPES = ('Architect', 'Contractor', 'Interior Designer', 'Carpenter', 'Engineer')



PROJECT_MIDDLES = [
    'house',
    'office',
    'business',
    'lobby',
    'municipal'
]

PROJECT_SUFFIXES = [
    'development',
    'renovation',
    'restoration',
    'remodel',
    'expansion',
    'addition'
]

def random_date(deadline=None):
    if deadline:
        return deadline - datetime.timedelta(days=random.randint(1, 90))
    return timezone.now() + datetime.timedelta(days=random.randint(60, 130))



def get_name_and_email():
    fake = Faker()
    name = fake.name()
    email = name.replace(' ', '')
    email = f'{email}@hotgmail.com'
    return [name, email]


def create_user(**kwargs):
    user_model: User = get_user_model()
    name, email = get_name_and_email()
    print('name = ', name)
    print('email = ', email)
    user = user_model.objects.create_user(
        email=email,
        password=PASSWORD,
        email_verified=True,
        is_active=True,
        demo=True,
        full_name=name,
        **kwargs
        )
    return user


def create_address(**kwargs):
    address_1 = kwargs.get('address1')
    address_2 = kwargs.get('address2')
    city = kwargs.get('city')
    state = kwargs.get('state')
    postal_code = kwargs.get('postalCode')
    try:
        address = Address.objects.get_or_create_address(
            address_line_1=address_1,
            address_line_2=address_2,
            city=city,
            state=state,
            postal_code=postal_code
            )
        return address
    except ValidationError:
        print('bad addres')
        return None


def create_group(user, address):
    fake = Faker()
    u_phone = fake.phone_number()
    u_phone = u_phone[:25] if len(u_phone) > 25 else u_phone
    ret_com_text = fake.paragraph(nb_sentences=4, variable_nb_sentences=True)
    print(ret_com_text)
    ret_com_name = fake.company() + ' demo'
    company = BaseGroup.objects.create_group(
        user=user,
        business_address=address,
        phone_number=u_phone,
        name=ret_com_name,
        info=ret_com_text
        )
    if isinstance(company, ProCompany):
        pick_serve = random.choice(SERVICE_TYPES)
        serv_obj = ServiceType.objects.get_or_create(label=pick_serve)[0]
        company.service = serv_obj
        company.save()
    for x in range(random.randint(0, 3)):
        create_employees(company)
    return company


def create_employees(company):
    if isinstance(company, ProCompany):
        user = create_user(is_pro=True)
    else:
        user = create_user(is_supplier=True)
    admin = random.choice([True, False])
    employee = BaseProfile.objects.create_profile(
        user=user,
        company=company,
        admin=admin
        )
    return employee


def create_project(user, address: Address):
    deadline = random_date()
    middle = random.choice(PROJECT_MIDDLES)
    suffix = random.choice(PROJECT_SUFFIXES)
    nickname = f'{address.city} {middle} {suffix}' if address else f'{middle} {suffix}'
    project = Project.objects.create_project(
        user=user,
        nickname=nickname,
        deadline=deadline
        )
    if address:
        project.address= address
        project.save()
    return project

def create_locations(company: RetailerCompany, address: Address):
    fake = Faker()
    u_phone: str = fake.phone_number()
    location = RetailerLocation.objects.create(
        company=company,
        address=address,
        approved_in_store_seller=True,
        phone_number=u_phone[:16] if len(u_phone) > 16 else u_phone
        )
    return location

@transaction.atomic
def create_demo_users():
    fake = Faker()
    user_count = 12
    retailer_count = 20
    pro_count = 20
    addresses_response = requests.get(ADDRESS_URL).json()
    addresses = addresses_response.get('addresses', [])
    addresses = list(addresses)
    random.shuffle(addresses)
    print('addresses length = ', len(addresses))
    for usernum in range(0, user_count):
        print(usernum)
        user = create_user()
        u_phone = fake.phone_number()
        prof = ConsumerProfile.objects.get_or_create(user=user)[0]
        prof.phone_number = u_phone
        prof.save()
        proj_num = random.randint(3,6)
        for num in range(0, proj_num):
            proj_add = addresses.pop()
            proj_add = create_address(**proj_add)
            project = create_project(user, proj_add)
            # create_assignments_and_tasks(project, product_ids)
        print('user name = ', user.full_name)
    for pro_num in range(0, pro_count):
        print('pro_count = ', pro_num)
        pro_user = create_user(is_pro=True)
        pro_address = addresses.pop()
        pro_address = create_address(**pro_address)
        pro_company = create_group(pro_user, pro_address)
        employee = ProEmployeeProfile.objects.create_profile(
            user=pro_user,
            company=pro_company
            )
        if pro_num == 0:
            employee.owner = True
            employee.save()
        for num in range(0, 3):
            proj_add = addresses.pop()
            proj_add = create_address(**proj_add)
            project = create_project(pro_user, proj_add)
            # create_assignments_and_tasks(project, product_ids)
        print('pro name = ', pro_user.full_name)
    for ret_num in range(0, retailer_count):
        ret_user = create_user(is_supplier=True)
        ret_address = addresses.pop()
        ret_address = create_address(**ret_address)
        ret_company = create_group(ret_user, ret_address)
        profile = RetailerEmployeeProfile.objects.create_profile(
            user=ret_user,
            company=ret_company
            )
        if ret_num == 0:
            profile.owner = True
            profile.save()
        for x in range(0, 3):
            loc_add = addresses.pop()
            loc_add = create_address(**loc_add)
            location = create_locations(ret_company, loc_add)
            # create_retailer_products(location, product_ids)
        print('ret name = ', ret_user.full_name)
