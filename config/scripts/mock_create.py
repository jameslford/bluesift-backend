import random
import datetime
import decimal
import requests
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from Accounts.models import User
from Addresses.models import Address
from Products.models import Product
from Profiles.models import ConsumerProfile, RetailerEmployeeProfile, ProEmployeeProfile, BaseProfile
from Groups.models import Company, ServiceType, ProCompany, RetailerCompany
from UserProductCollections.models import RetailerLocation, BaseProject
from UserProducts.models import RetailerProduct, ProjectProduct
from Schedule.models import ProductAssignment, ProjectTask, ConsumerCollaborator, ProCollaborator

# ADDRESS_URL = 'https://raw.githubusercontent.com/EthanRBrown/rrad/master/addresses-us-100.json'
ADDRESS_URL = 'https://raw.githubusercontent.com/EthanRBrown/rrad/master/addresses-us-all.min.json'
PASSWORD = '0gat_surfer'
SERVICE_TYPES = ('Architect', 'Contractor', 'Interior Designer', 'Carpenter', 'Engineer')

ROOMS = [
    'bathroom',
    'kitchen',
    'office',
    'den',
    'library',
    'deck',
    'patio',
    'living room',
    'basement',
]

APPLICATIONS = [
    'walls',
    'floor',
    'counter',
    'desk wrap',
    'bookshelf covering',
    'fireplace interior',
    'mantle',
    'stand'
]

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

SUB_TASKS = [
    'clean',
    'electrical',
    'plumbing',
    'painting',
    'framing',
    'finish work',
    'millwork',
    'demo'
]


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
    address = Address.objects.get_or_create_address(
        address_line_1=address_1,
        address_line_2=address_2,
        city=city,
        state=state,
        postal_code=postal_code
        )
    return address


def create_company(user, address):
    fake = Faker()
    u_phone = fake.phone_number()
    u_phone = u_phone[:25] if len(u_phone) > 25 else u_phone
    ret_com_text = fake.paragraph(nb_sentences=4, variable_nb_sentences=True)
    print(ret_com_text)
    ret_com_name = fake.company() + ' demo'
    company = Company.objects.create_company(
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


def random_date(deadline=None):
    if deadline:
        return deadline - datetime.timedelta(days=random.randint(1, 30))
    return timezone.now() + datetime.timedelta(days=random.randint(60, 130))


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
    nickname = f'{address.city} {middle} {suffix}'
    return BaseProject.objects.create_project(
        user=user,
        nickname=nickname,
        address_pk=address.pk,
        deadline=deadline
        )


def create_assignments_and_tasks(project: BaseProject, _product_ids):
    prod_ids = list(_product_ids)
    rooms = ROOMS.copy()
    applications = APPLICATIONS.copy()
    for x in range(random.randint(8, 20)):
        select_id = random.choice(prod_ids)
        del prod_ids[prod_ids.index(select_id)]
        product = Product.objects.get(pk=select_id)
        ProjectProduct.objects.create(
            product=product,
            project=project
            )
        assignment_choice = random.choice([True, False])
        if assignment_choice and rooms:
            quantity = random.randint(30, 200)
            room = random.choice(rooms)
            index = rooms.index(room)
            del rooms[index]
            application = random.choice(applications)
            assignment_name = f'{room} {application}'
            supplier = product.priced.all().first()
            supplier = supplier.retailer if supplier else None
            assignment = ProductAssignment.objects.create(
                name=assignment_name,
                quantity_needed=quantity,
                product=product,
                project=project,
                supplier=supplier
                )
            parent_task = ProjectTask.objects.create(
                name=room,
                project=project
                )
            child_name = f'{application} install'
            child_start = project.deadline - datetime.timedelta(days=20)
            ProjectTask.objects.create(
                name=child_name,
                product=assignment,
                project=project,
                duration=datetime.timedelta(days=random.randint(3, 9)),
                start_date=child_start,
                parent=parent_task
                )
            for stask in random.sample(SUB_TASKS, 3):
                ProjectTask.objects.create(
                    name=stask,
                    parent=parent_task,
                    duration=datetime.timedelta(days=random.randint(3, 9)),
                    start_date=random_date(project.deadline),
                    project=project
                    )


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


def create_retailer_products(location: RetailerLocation, _product_ids):
    product_ids = _product_ids
    max_count = product_ids.count()
    rang_int = random.randint(10, (max_count // 20))
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


@transaction.atomic
def create_demo_users():
    fake = Faker()
    user_count = 10
    retailer_count = 14
    pro_count = 14
    addresses_response = requests.get(ADDRESS_URL).json()
    addresses = addresses_response.get('addresses', [])
    addresses = list(addresses)
    random.shuffle(addresses)
    print('addresses length = ', len(addresses))
    product_ids = Product.objects.values_list('pk', flat=True)
    for usernum in range(0, user_count):
        user = create_user()
        u_phone = fake.phone_number()
        ConsumerProfile.objects.create_profile(
            user=user,
            phone_number=u_phone
            )
        for x in range(0, 3):
            proj_add = addresses.pop()
            proj_add = create_address(**proj_add)
            project = create_project(user, proj_add)
            create_assignments_and_tasks(project, product_ids)
        print('user name = ', user.full_name)
    for pro_num in range(0, pro_count):
        pro_user = create_user(is_pro=True)
        pro_address = addresses.pop()
        pro_address = create_address(**pro_address)
        pro_company = create_company(pro_user, pro_address)
        ProEmployeeProfile.objects.create_profile(
            user=pro_user,
            owner=True,
            company=pro_company
            )
        for x in range(0, 3):
            proj_add = addresses.pop()
            proj_add = create_address(**proj_add)
            project = create_project(pro_user, proj_add)
            create_assignments_and_tasks(project, product_ids)
        print(pro_user.full_name)
    for ret_num in range(0, retailer_count):
        ret_user = create_user(is_supplier=True)
        ret_address = addresses.pop()
        ret_address = create_address(**ret_address)
        ret_company = create_company(ret_user, ret_address)
        profile = RetailerEmployeeProfile.objects.create_profile(
            user=ret_user,
            owner=True,
            company=ret_company
            )
        for x in range(0, 3):
            loc_add = addresses.pop()
            loc_add = create_address(**loc_add)
            location = create_locations(ret_company, loc_add)
            create_retailer_products(location, product_ids)
        print(ret_user.full_name)
