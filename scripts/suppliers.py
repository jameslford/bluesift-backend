import random
from typing import List
import datetime
import decimal
from faker import Faker
from django.core.files import File
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from Suppliers.models import SupplierLocation, SupplierProduct, SupplierCompany
from Products.models import Product
from Profiles.models import SupplierEmployeeProfile
from Addresses.models import Address
from Profiles.models import BaseProfile
from .demo_data import create_user, choose_image


def generate_retailers(address_group):
    number = random.randint(2, 5)
    employees = [create_user(is_supplier=True) for num in range(0, number)]
    ret_company = create_supplier_company(employees[0][0], address_group[0])
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
        create_locations(ret_company, loc_add)


def create_employees(company):
    user = create_user(is_supplier=True)
    admin = random.choice([True, False])
    employee = BaseProfile.objects.create_profile(
        user=user[0], company=company, company_admin=admin
    )
    return employee


def create_locations(company: SupplierCompany, address: Address):
    fake = Faker()
    u_phone: str = fake.phone_number()
    location = SupplierLocation.objects.create(
        company=company,
        address=address,
        approved_in_store_seller=True,
        phone_number=u_phone[:16] if len(u_phone) > 16 else u_phone,
    )
    return location


def create_supplier_company(user, address):
    fake = Faker()
    u_phone = fake.phone_number()
    u_phone = u_phone[:25] if len(u_phone) > 25 else u_phone
    ret_com_text = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
    print(ret_com_text)
    ret_com_name = fake.company() + " demo"
    try:
        company = SupplierCompany.objects.create_group(
            user=user,
            business_address=address,
            phone_number=u_phone,
            name=ret_com_name,
            info=ret_com_text,
        )
        for _ in range(random.randint(1, 3)):
            create_employees(company)
        return company
    except IntegrityError:
        create_supplier_company(user, address)


def refresh_supplier_products():
    user_model = get_user_model()
    demo_suppliers = user_model.objects.filter(demo=True, is_supplier=True).values_list(
        "profile__pk", flat=True
    )
    demo_sup_profiles = (
        SupplierEmployeeProfile.objects.filter(pk__in=demo_suppliers)
        .values_list("company__pk", flat=True)
        .distinct()
    )
    locations = SupplierLocation.objects.filter(company__pk__in=demo_sup_profiles)
    SupplierProduct.objects.filter(location__company__pk__in=demo_sup_profiles).delete()
    min_count = 30
    for ind, location in enumerate(locations):
        print(str(ind) + " out of " + str(int(locations.count())) + "locations")
        if location.products.all().count() >= min_count:
            continue
        products: List[Product] = list(Product.objects.all())
        max_count = (len(products) // 18) + min_count
        rang_int = random.randint(min_count, max_count)
        for _ in range(rang_int):
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
                product=select_product, location=location
            )[0]
            sup_prod.units_available_in_store = units_available
            sup_prod.units_per_order = units_per_order
            sup_prod.publish_in_store_price = True
            sup_prod.in_store_ppu = price
            sup_prod.lead_time_ts = datetime.timedelta(days=lead_time)
            sup_prod.offer_installation = offer_install
            sup_prod.save()
