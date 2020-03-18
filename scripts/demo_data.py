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
from Profiles.models import ConsumerProfile, SupplierEmployeeProfile, BaseProfile, LibraryProduct
from Groups.models import SupplierCompany
from Suppliers.models import SupplierLocation, SupplierProduct
from Projects.models import Project, ProjectTask, ProjectProduct

ADDRESS_URL = 'https://raw.githubusercontent.com/EthanRBrown/rrad/master/addresses-us-all.min.json'
PASSWORD = '0gat_surfer'
SERVICE_TYPES = ('Architect', 'Contractor', 'Interior Designer', 'Carpenter', 'Engineer')



PROJECT_MIDDLES = [
    'house',
    'office',
    'business',
    'lobby',
    'municipal',
    'restaurant',
    'store',
    'park',
    'annex'
]

PROJECT_SUFFIXES = [
    'development',
    'renovation',
    'restoration',
    'remodel',
    'expansion',
    'addition'
]


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


SUB_TASKS = [
    'demo',
    'plumbing',
    'electrical',
    'framing',
    'finish work',
    'painting',
    'millwork',
    'clean',
    ]


def create_demo_users():
    # create_addresses()
    main()





def generate_address_groups():
    addresses = Address.objects.filter(demo=True)
    exclude_pks = []
    return_groups = []
    for address in addresses:
        if address.pk in exclude_pks:
            continue
        number = random.randint(2, 4)
        closest = address.find_closest_others()
        adds = []
        # for num, close in zip(range(0, number), closest):
            # for close in closest:
        for num in range(0, number):
            for close in closest:
                if close.pk in exclude_pks:
                    continue
                adds.append(close)
                exclude_pks.append(close.pk)
                break
        adds.append(address)
        exclude_pks.append(address.pk)
        return_groups.append(adds)
    print(return_groups)
    return return_groups


    # address_pks = list(Address.objects.filter(demo=True).values_list('pk', flat=True))
    # print(address_pks)
    # random.shuffle(address_pks)

def _generate_users(address_group):
    user = __create_user()
    # pylint: disable=undefined-variable

    u_phone = Faker().phone_number()
    prof = ConsumerProfile.objects.get_or_create(user=user)[0]
    prof.phone_number = u_phone
    prof.save()
    for address in address_group:
        # address = Address.objects.get(pk=apk)
        __create_project(user, address)


def _generate_retailers(address_group):
    # comp_address_pk = address_pks.pop()
    # comp_address = Address.objects.get(pk=comp_address_pk)
    # ret_user = __create_user(is_supplier=True)
    number = random.randint(2, 8)
    # comp_address = Address.objects.get(pk=address_group[0])
    employees = [__create_user(is_supplier=True) for num in range(0, number)]
    ret_company = __create_supplier_company(employees[0], address_group[0])
    print('ret_company = ', ret_company)
    for ind, emp in enumerate(employees):
        profile = SupplierEmployeeProfile.objects.create_profile(
            user=emp,
            company=ret_company
            )
        if ind == 0:
            profile.company_owner = True
            profile.save()
    for loc_add in address_group:
        # loc_add = Address.objects.get(pk=apk)
        __create_locations(ret_company, loc_add)



# @transaction.atomic
def main():
    address_groups = generate_address_groups()
    for group in address_groups:
        choice = random.randint(4, 6)
        if choice > 4:
            _generate_retailers(group)
        else:
            _generate_users(group)





def __create_address(**kwargs):
    address_1 = kwargs.get('address1')
    address_2 = kwargs.get('address2')
    city = kwargs.get('city')
    state = kwargs.get('state')
    postal_code = kwargs.get('postalCode')
    try:
        return Address.objects.get_or_create_address(
            address_line_1=address_1,
            address_line_2=address_2,
            city=city,
            state=state,
            postal_code=postal_code,
            demo=True
            )
    except (ValidationError, IndexError):
        print('bad addres')
        return None


def create_addresses():
    addresses_response = requests.get(ADDRESS_URL).json()
    addresses = addresses_response.get('addresses', [])
    addresses = list(addresses)
    for address in addresses:
        __create_address(**address)

@transaction.atomic
def add_additonal():
    __create_supplier_products()
    __create_group_products()


def __add_group_products(profile: ConsumerProfile):
    print('adding products to ', profile.name())
    products = list(Product.objects.values_list('pk', flat=True))
    min_prod = 20
    max_products = random.randint(min_prod, 40)
    if profile.products.all().count() >= min_prod:
        print('products already assigned')
        return
    project_products = []
    for num in range(max_products):
        index = random.choice(products)
        index = products.index(index)
        product = products.pop(index)
        product = Product.objects.get(pk=product)
        pprod = LibraryProduct.objects.create(product=product, owner=profile)
        project_products.append(pprod)
    tasks = ProjectTask.objects.filter(project__owner=profile)
    for pps, pts in zip(project_products, tasks):
        prod = ProjectProduct.objects.create(linked_tasks=pts, product=pps)
        prod.quantity_needed = random.randint(10, 100)
        if random.randint(0, 10) > 6:
            prod.supplier_product = prod.product.priced.first()
            prod.procured = random.choice([True, False])
        prod.save()



def __create_group_products():
    consumer_profiles = ConsumerProfile.objects.filter(user__demo=True)
    for prof in consumer_profiles:
        __add_group_products(prof)


def create_parent_tasks():
    projects: List[Project] = Project.objects.all()
    for project in projects:
        print('creating parent tasks for ', project.nickname)
        rooms = ROOMS.copy()
        total_rooms = len(rooms) - 3
        products = [prod.product for prod in project.owner.products.all()]
        task_max = random.randint(3, total_rooms)
        task_count = range(task_max)
        # deadline = project.deadline
        for num in task_count:
            add_assignment = random.choice([True, False])
            task_name = random.choice(rooms)
            index = rooms.index(task_name)
            task_name = rooms.pop(index)
            task = ProjectTask(project=project)
            task.name = task_name
            # duration = random.uniform(3, 20)
            # start_date = __random_date(deadline)
            # duration = datetime.timedelta(days=duration)
            # progress = random.randint(0, 100)
            # task.start_date = start_date
            # task.duration = duration
            # task.progress = progress
            if add_assignment:
                prod = random.choice(products)
                index = products.index(prod)
                task.product = products.pop(index)
                task.quantity_needed = random.randint(30, 300)
                task.procured = random.choice([True, False])
            task.save()
        project_tasks = list(project.tasks.all())
        while len(project_tasks) > 2:
            # pred = random.randint(0, 10)
            # print('pred likelihood = ', pred, 'len tasks = ', len(project_tasks))
            # if pred > 3:
            rec_task = project_tasks.pop(0)
            pred_task = project_tasks.pop(1)
            rec_task.predecessor = pred_task
            rec_task.save()






def create_child_tasks():
    tasks: List[ProjectTask] = ProjectTask.objects.filter(level=0)
    for task in tasks:
        print('creating children for ', task.name)
        # children_count = random.randint(2, 6)
        sub_tasks = SUB_TASKS.copy()
        current_child = None
        for child in sub_tasks:
            # sub_name = random.choice(sub_tasks)
            # index = sub_tasks.index(sub_name)
            # sub = sub_tasks.pop(index)
            cont = random.randint(0, 10)
            if cont < 4:
                continue
            # duration = random.uniform(3, 5)
            duration = random.randint(3, 5)
            # tdelt = random.randint(0, 6)
            child_task = ProjectTask()
            child_task.parent = task
            child_task.name = child
            child_task.project = task.project
            child_task.duration = datetime.timedelta(days=duration)
            if current_child and random.randint(0, 10) > 4:
                child_task.predecessor = current_child
            try:
                child_task.save()
                current_child = child_task
            except ValidationError:
                continue


def __create_supplier_products():
    locations: List[SupplierLocation] = SupplierLocation.objects.all()
    min_count = 30
    for location in locations:
        if location.products.all().count() >= min_count:
            print('products already assigned')
            continue
        products: List[Product] = list(Product.objects.all())
        max_count = len(products)
        max_count = (max_count // 18) + min_count
        rang_int = random.randint(min_count, max_count)
        for num in range(rang_int):
            print(num, rang_int)
            price = random.uniform(1, 10)
            price = round(float(price), 2)
            price = decimal.Decimal(price)
            units_available = random.randint(10, 60)
            units_per_order = decimal.Decimal(3.5)
            select_product = random.choice(products)
            index = products.index(select_product)
            select_product = products.pop(index)
            lead_time = random.randint(1, 14)
            offer_install = random.choice([True, False])
            sup_prod: SupplierProduct = SupplierProduct.objects.get_or_create(
                product=select_product,
                location=location
                )[0]
            sup_prod.units_available_in_store = units_available
            sup_prod.units_per_order = units_per_order
            sup_prod.publish_in_store_price = True
            sup_prod.in_store_ppu = price
            sup_prod.lead_time_ts = datetime.timedelta(days=lead_time)
            sup_prod.offer_installation = offer_install
            print(f'retailer product {sup_prod.offer_installation} created')
            sup_prod.save()


def __random_date(deadline=None):
    if deadline:
        return deadline - datetime.timedelta(days=random.randint(1, 90))
    return timezone.now() + datetime.timedelta(days=random.randint(20, 40))

def __get_name_and_email():
    fake = Faker()
    name = fake.name()
    email = name.replace(' ', '')
    email = f'{email}@hotgmail.com'
    return [name, email]


def __create_user(**kwargs):
    user_model: User = get_user_model()
    name, email = __get_name_and_email()
    is_supplier = kwargs.get('is_supplier', False)
    print('name = ', name)
    print('email = ', email)
    user = user_model.objects.filter(email=email).first()
    if user:
        return __create_user(**kwargs)
    user = user_model.objects.create_user(
        email=email,
        password=PASSWORD,
        email_verified=True,
        is_active=True,
        demo=True,
        full_name=name,
        is_supplier=is_supplier
        # **kwargs
        )
    return user



def __create_supplier_company(user, address):
    fake = Faker()
    u_phone = fake.phone_number()
    u_phone = u_phone[:25] if len(u_phone) > 25 else u_phone
    ret_com_text = fake.paragraph(nb_sentences=4, variable_nb_sentences=True)
    print(ret_com_text)
    ret_com_name = fake.company() + ' demo'
    try:
        company = SupplierCompany.objects.create_group(
            user=user,
            business_address=address,
            phone_number=u_phone,
            name=ret_com_name,
            info=ret_com_text
            )
        for x in range(random.randint(0, 3)):
            __create_employees(company)
        return company
    except IntegrityError:
        __create_supplier_company(user, address)



def __create_employees(company):
    user = __create_user(is_supplier=True)
    admin = random.choice([True, False])
    employee = BaseProfile.objects.create_profile(
        user=user,
        company=company,
        company_admin=admin
        )
    return employee


def __create_project(user: User, address: Address):
    deadline = __random_date()
    middle = random.choice(PROJECT_MIDDLES)
    suffix = random.choice(PROJECT_SUFFIXES)
    nickname = f'{address.get_short_name()} {middle} {suffix}' if address else f'{middle} {suffix}'
    try:
        project = Project.objects.create_project(
            user=user,
            nickname=nickname,
            deadline=deadline
            )
        if address:
            project.address = address
            project.save()
        return project
    except IntegrityError:
        return None

def __create_locations(company: SupplierCompany, address: Address):
    fake = Faker()
    u_phone: str = fake.phone_number()
    location = SupplierLocation.objects.create(
        company=company,
        address=address,
        approved_in_store_seller=True,
        phone_number=u_phone[:16] if len(u_phone) > 16 else u_phone
        )
    return location

