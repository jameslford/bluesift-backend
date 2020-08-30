import os
import random
import datetime
from faker import Faker
from django.core.files import File
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from config.celery import app
from Addresses.models import Address
from Suppliers.models import SupplierLocation
from Projects.models import Project
from .addresses import create_addresses, generate_address_groups

PASSWORD = "0gat_surfer"


@app.task
@transaction.atomic
def auto_refresh():
    from Profiles.models import SupplierEmployeeProfile, ConsumerProfile

    allowed = bool(settings.ENVIRONMENT == "staging" or settings.ENVIRONMENT == "local")
    if not allowed:
        return
    fake_employees = SupplierEmployeeProfile.objects.filter(user__demo=True)
    fake_companies = set(emp.company.pk for emp in fake_employees)
    fake_locations = SupplierLocation.objects.filter(company__pk__in=fake_companies)
    for loc in fake_locations:
        loc.refresh_demo_view_records()
    user_model = get_user_model()
    demos = user_model.objects.filter(demo=True)
    for demo in demos:
        cons_profile = ConsumerProfile.objects.filter(user=demo).first()
        if cons_profile:
            project: Project = Project.objects.filter(owner=demo.profile)
            project.tasks.delete()
            project.create_fake_parent_tasks()
            project.create_fake_children_task()


def delete_fake():
    from Groups.models import SupplierCompany
    from Profiles.models import SupplierEmployeeProfile, ConsumerProfile

    user_model = get_user_model()
    fake_comps = (
        SupplierEmployeeProfile.objects.filter(user__demo=True)
        .values_list("company__pk", flat=True)
        .distinct()
    )
    SupplierCompany.objects.filter(pk__in=fake_comps).delete()
    demos = user_model.objects.filter(demo=True)
    for demo in demos:
        cons_profile = ConsumerProfile.objects.filter(user=demo).first()
        if cons_profile:
            Project.objects.filter(owner=demo.profile).delete()
        demo.delete()


@transaction.atomic
def full_refresh():
    delete_fake()
    if Address.objects.all().count() < 150:
        create_addresses()
    address_groups = generate_address_groups()
    for group in address_groups:
        choice = random.randint(4, 6)
        if choice > 4:
            generate_retailers(group)
        else:
            generate_users(group)


def random_deadline(deadline=None):
    if deadline:
        return deadline - datetime.timedelta(days=random.randint(1, 90))
    return timezone.now() + datetime.timedelta(days=random.randint(20, 40))


def __get_name_and_email():
    fake = Faker()
    gender = random.choice(["male", "female"])
    if gender == "male":
        name = fake.name_male()
    else:
        name = fake.name_female()
    email = name.replace(" ", "")
    email = f"{email}@hotgmail.com"
    return [name, email, gender]


def create_user(**kwargs):
    user_model = get_user_model()
    name, email, gender = __get_name_and_email()
    is_supplier = kwargs.get("is_supplier", False)
    user = user_model.objects.filter(email=email).first()
    if user:
        return create_user(**kwargs)
    user = user_model.objects.create_user(
        email=email,
        password=PASSWORD,
        email_verified=True,
        is_active=True,
        demo=True,
        full_name=name,
        is_supplier=is_supplier,
    )
    return [user, gender]


def choose_image(gender: str):
    if os.name == "nt":
        path = f"{os.getcwd()}\\data\\people_img\\{gender}\\"
    else:
        path = f"{os.getcwd()}/data/people_img/{gender}/"
    return path + random.choice(os.listdir(path))


def generate_users(address_group):
    from Profiles.models import ConsumerProfile

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
        project: Project = Project.create_demo_project(user, address)
        project.create_fake_parent_tasks()
        project.create_fake_children_task()


def generate_retailers(address_group):
    from Groups.models import SupplierCompany
    from Profiles.models import SupplierEmployeeProfile

    number = random.randint(2, 5)
    employees = [create_user(is_supplier=True) for num in range(0, number)]
    ret_company = SupplierCompany.create_demo_supplier_company(
        employees[0][0], address_group[0]
    )
    if not ret_company:
        return
    for ind, emp in enumerate(employees):
        user = emp[0]
        gender = emp[1]
        profile = SupplierEmployeeProfile.objects.create_profile(
            user=user, company=ret_company
        )
        title_choices = [
            "",
            "Inventory Manager",
            "Sales Associate",
            "Receptionist",
            "Market Manager",
        ]
        img = open(choose_image(gender), "rb")
        file = File(img)
        profile.avatar.save(user.email, file, True)
        if ind == 0:
            profile.company_owner = True
            profile.title = "Owner"
        else:
            profile.title = random.choice(title_choices)
            img.close()
        profile.save()
    for loc_add in address_group:
        location: SupplierLocation = create_locations(ret_company, loc_add)
        location.refresh_demo_view_records()


def create_locations(company, address: Address):
    fake = Faker()
    u_phone: str = fake.phone_number()
    location = SupplierLocation.objects.create(
        company=company,
        address=address,
        approved_in_store_seller=True,
        phone_number=u_phone[:16] if len(u_phone) > 16 else u_phone,
    )
    return location

