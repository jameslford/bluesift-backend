import random
from typing import List
import datetime
from faker import Faker
from django.utils import timezone
from django.core.files import File
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from Products.models import Product
from Profiles.models import ConsumerProfile, LibraryProduct
from Projects.models import ProjectTask, Project, ProjectProduct
from Accounts.models import User
from Addresses.models import Address
from .demo_data import random_date, create_user, choose_image

SERVICE_TYPES = (
    "Architect",
    "Contractor",
    "Interior Designer",
    "Carpenter",
    "Engineer",
)


PROJECT_MIDDLES = [
    "house",
    "office",
    "business",
    "lobby",
    "municipal",
    "restaurant",
    "store",
    "park",
    "annex",
]

PROJECT_SUFFIXES = [
    "development",
    "renovation",
    "restoration",
    "remodel",
    "expansion",
    "addition",
]


ROOMS = [
    "bathroom",
    "kitchen",
    "office",
    "den",
    "library",
    "deck",
    "patio",
    "living room",
    "basement",
]

APPLICATIONS = [
    "walls",
    "floor",
    "counter",
    "desk wrap",
    "bookshelf covering",
    "fireplace interior",
    "mantle",
    "stand",
]


SUB_TASKS = [
    "demo",
    "plumbing",
    "electrical",
    "framing",
    "finish work",
    "painting",
    "millwork",
    "clean",
]


def generate_users(address_group):
    user, gender = create_user()
    u_phone = Faker().phone_number()
    img = open(choose_image(gender), "rb")
    file = File(img)
    prof = ConsumerProfile.objects.get_or_create(user=user)[0]
    prof.avatar.save(user.email, file)
    prof.avatar.image = img
    img.close()
    prof.phone_number = u_phone
    prof.save()
    for address in address_group:
        create_project(user, address)


def create_project(user: User, address: Address):
    deadline = random_date()
    middle = random.choice(PROJECT_MIDDLES)
    suffix = random.choice(PROJECT_SUFFIXES)
    nickname = (
        f"{address.get_short_name()} {middle} {suffix}"
        if address
        else f"{middle} {suffix}"
    )
    try:
        project = Project.objects.create_project(
            user=user, nickname=nickname, deadline=deadline
        )
        if address:
            project.address = address
            project.save()
        return project
    except IntegrityError:
        return None


def add_group_products():
    for profile in ConsumerProfile.objects.filter(user__demo=True):
        products = list(Product.objects.values_list("pk", flat=True))
        min_prod = 20
        max_products = random.randint(min_prod, 40)
        if profile.products.all().count() >= min_prod:
            print("products already assigned")
            continue
        project_products = []
        for _ in range(max_products):
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


def add_task_products():
    pprods = ProjectProduct.objects.all()
    for p in pprods:
        p.delete()
    projects = Project.objects.all()
    for project in projects:
        project.deadline = timezone.now() + datetime.timedelta(
            days=random.randint(20, 40)
        )
        project.save()
        tasks = project.tasks.all()
        products = project.owner.products.all()
        for task, product in zip(tasks, products):
            prod = ProjectProduct.objects.create(linked_tasks=task, product=product)
            prod.quantity_needed = random.randint(10, 100)
            if random.randint(0, 10) > 6:
                prod.supplier_product = prod.product.product.priced.first()
                prod.procured = random.choice([True, False])
            prod.save()


def create_parent_tasks():
    projects: List[Project] = Project.objects.all()
    for project in projects:
        print("creating parent tasks for ", project.nickname)
        rooms = ROOMS.copy()
        total_rooms = len(rooms) - 4
        products = [prod.product for prod in project.owner.products.all()]
        task_count = range(random.randint(3, total_rooms))
        for _ in task_count:
            add_assignment = random.choice([True, False])
            task_name = random.choice(rooms)
            task_name = rooms.pop(rooms.index(task_name))
            task = ProjectTask(project=project)
            task.name = task_name
            if add_assignment:
                prod = random.choice(products)
                index = products.index(prod)
                task.product = products.pop(index)
                task.quantity_needed = random.randint(30, 300)
                task.procured = random.choice([True, False])
            task.save()
        project_tasks = list(project.tasks.all())
        while len(project_tasks) > 2:
            rec_task = project_tasks.pop(0)
            pred_task = project_tasks.pop(1)
            rec_task.predecessor = pred_task
            rec_task.save()


def create_child_tasks():
    tasks: List[ProjectTask] = ProjectTask.objects.filter(level=0)
    for task in tasks:
        print("creating children for ", task.name)
        sub_tasks = SUB_TASKS.copy()
        current_child = None
        for child in sub_tasks:
            cont = random.randint(0, 10)
            if cont < 4:
                continue
            duration = random.randint(3, 5)
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
