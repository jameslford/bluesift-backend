import random
import datetime
import decimal
from typing import List
from django.db import transaction
from Products.models import Product
from Profiles.models import ConsumerProfile
from Projects.models import Project, LibraryProduct, ProjectTask
from Suppliers.models import SupplierLocation, SupplierProduct
from .mock_create import random_date

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
    'clean',
    'electrical',
    'plumbing',
    'painting',
    'framing',
    'finish work',
    'millwork',
    'demo'
    ]

@transaction.atomic
def add_group_products(profile: ConsumerProfile):
    print('adding products to ', profile.name)
    products = list(Product.objects.values_list('pk', flat=True))
    min_prod = 20
    max_products = random.randint(min_prod, 40)
    if profile.products.all().count() >= min_prod:
        print('products already assigned')
        return
    for num in range(max_products):
        index = random.choice(products)
        index = products.index(index)
        product = products.pop(index)
        product = Product.objects.get(pk=product)
        LibraryProduct.objects.create(product=product, owner=profile)


@transaction.atomic
def create_group_products():
    consumer_profiles = ConsumerProfile.objects.filter(user__demo=True)
    for prof in consumer_profiles:
        add_group_products(prof)

@transaction.atomic
def create_parent_tasks():
    projects: List[Project] = Project.objects.all()
    for project in projects:
        print('creating parent tasks for ', project.nickname)
        rooms = ROOMS.copy()
        total_rooms = len(rooms)
        products = [prod.product for prod in project.owner.products.all()]
        task_max = random.randint(3, total_rooms)
        task_count = range(task_max)
        deadline = project.deadline
        for num in task_count:
            add_assignment = random.choice([True, False])
            task_name = random.choice(rooms)
            index = rooms.index(task_name)
            duration = random.uniform(3, 18)
            task_name = rooms.pop(index)
            start_date = random_date(deadline)
            duration = datetime.timedelta(duration)
            progress = random.randint(0, 100)
            task = ProjectTask(project=project)
            task.name = task_name
            task.start_date = start_date
            task.duration = duration
            task.progress = progress
            if add_assignment:
                prod = random.choice(products)
                index = products.index(prod)
                task.product = products.pop(index)
                task.quantity_needed = random.randint(30, 300)
                task.procured = random.choice([True, False])
            task.save()

@transaction.atomic
def create_child_tasks():
    tasks: List[ProjectTask] = ProjectTask.objects.all()
    for task in tasks:
        print('creating children for ', task.name)
        children_count = random.randint(2, 6)
        sub_tasks = SUB_TASKS.copy()
        for child in range(children_count):
            sub_name = random.choice(sub_tasks)
            index = sub_tasks.index(sub_name)
            sub = sub_tasks.pop(index)
            duration = random.uniform(3, 5)
            tdelt = random.randint(0, 6)
            child_task = ProjectTask()
            child_task.name = sub
            child_task.parent = task
            child_task.duration = datetime.timedelta(duration)
            child_task.progress = random.randint(0, 100)
            child_task.start_date = task.start_date + datetime.timedelta(tdelt)

@transaction.atomic
def create_retailer_products():
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
                retailer=location
                )[0]
            sup_prod.units_available_in_store = units_available
            sup_prod.units_per_order = units_per_order
            sup_prod.publish_in_store_price = True
            sup_prod.in_store_ppu = price
            sup_prod.lead_time_ts = datetime.timedelta(days=lead_time)
            sup_prod.offer_installation = offer_install
            print(f'retailer product {sup_prod.offer_installation} created')
            sup_prod.save()


def add_additonal():
    create_retailer_products()
    create_group_products()
    create_parent_tasks()
    create_child_tasks()
