import os
import random
import datetime
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model
from Accounts.models import User


PASSWORD = "0gat_surfer"


def random_date(deadline=None):
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
    user_model: User = get_user_model()
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
