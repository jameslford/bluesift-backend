import random
import datetime
import decimal
from Products.models import Product
from Projects.models import BaseProject, ProjectProduct, ProductAssignment, ProjectTask
from Retailers.models import RetailerLocation, RetailerProduct
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


def create_tasks():
    applications = APPLICATIONS.copy()
    rooms = ROOMS.copy()
    projects = BaseProject.objects.all()
    for project in projects:
        products = ProductAssignment.objects.filter(project=project)
        for product in products:
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


def create_assignments():
    prod_ids = list(Product.objects.values_list('pk', flat=True))
    projects = BaseProject.objects.all()
    for project in projects:
        for num in range(random.randint(8, 20)):
            select_id = random.choice(prod_ids)
            del prod_ids[prod_ids.index(select_id)]
            product = Product.objects.get(pk=select_id)
            ProjectProduct.objects.create(
                product=product,
                project=project
                )


def create_retailer_products():
    locations = RetailerLocation.objects.all()
    for location in locations:
        product_ids = list(Product.objects.values_list('pk', flat=True))
        max_count = product_ids.count()
        rang_int = random.randint(10, (max_count // 20))
        location_prod_ids = list(product_ids)
        for num in range(rang_int):
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



def add_additonal():
    create_retailer_products()
    create_assignments()
    create_tasks()