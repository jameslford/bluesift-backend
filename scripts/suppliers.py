import decimal
import random
from typing import List
import datetime
from faker import Faker
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from Suppliers.models import SupplierLocation, SupplierProduct, SupplierCompany
from Products.models import Product
from Profiles.models import SupplierEmployeeProfile
from Addresses.models import Address
from Profiles.models import BaseProfile
from .demo_data import create_user


def _generate_retailers(address_group):
    number = random.randint(2, 7)
    employees = [create_user(is_supplier=True) for num in range(0, number)]
    ret_company = __create_supplier_company(employees[0], address_group[0])
    if not ret_company:
        return
    for ind, emp in enumerate(employees):
        profile = SupplierEmployeeProfile.objects.create_profile(
            user=emp, company=ret_company
        )
        if ind == 0:
            profile.company_owner = True
            profile.save()
    for loc_add in address_group:
        __create_locations(ret_company, loc_add)

    # user_model = get_user_model()
    # demo_suppliers = user_model.objects.filter(demo=True, is_supplier=True).values_list(
    #     "profile__pk", flat=True
    # )
    # demo_sup_profiles = (
    #     SupplierEmployeeProfile.objects.filter(pk__in=demo_suppliers)
    #     .values_list("company__pk", flat=True)
    #     .distinct()
    # )
    # demo_sup_prods = SupplierProduct.objects.filter(
    #     location__company__pk__in=demo_sup_profiles
    # ).delete()
    # create_supplier_products()


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
        for num in range(rang_int):
            print(num + " / " + rang_int)
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


def __create_supplier_company(user, address):
    fake = Faker()
    u_phone = fake.phone_number()
    u_phone = u_phone[:25] if len(u_phone) > 25 else u_phone
    ret_com_text = fake.paragraph(nb_sentences=4, variable_nb_sentences=True)
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
        for x in range(random.randint(0, 3)):
            __create_employees(company)
        return company
    except IntegrityError:
        __create_supplier_company(user, address)


def __create_locations(company: SupplierCompany, address: Address):
    fake = Faker()
    u_phone: str = fake.phone_number()
    location = SupplierLocation.objects.create(
        company=company,
        address=address,
        approved_in_store_seller=True,
        phone_number=u_phone[:16] if len(u_phone) > 16 else u_phone,
    )
    return location


def __create_employees(company):
    user = create_user(is_supplier=True)
    admin = random.choice([True, False])
    employee = BaseProfile.objects.create_profile(
        user=user, company=company, company_admin=admin
    )
    return employee
