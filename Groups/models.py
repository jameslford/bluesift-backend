import random
from faker import Faker
from django.db import models, IntegrityError
from model_utils.managers import InheritanceManager
from Addresses.models import Address
from Plans.models import SupplierPlan
from scripts.demo_data import create_user


class SupplierGroupManager(models.Manager):
    def create_group(self, user, **kwargs):
        if user.is_supplier:
            return SupplierCompany.objects.get_or_create(**kwargs)[0]
        return

    def delete_group(self, user):
        profile = user.get_profile()
        if user.is_supplier and not profile.owner:
            return
        group = user.get_group()
        group.delete()
        return

    # def edit_group(self, user, **kwargs):
    #     if not user.is_supplier:
    #         return
    #     profile = user.get_profile()
    #     if not (profile.owner or profile.admin):
    #         return
    # company = user.get_group()
    # name = kwargs.get('name')


class SupplierCompany(models.Model):
    name = models.CharField(max_length=40, unique=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    business_address = models.OneToOneField(
        Address, null=True, on_delete=models.SET_NULL
    )
    email_verified = models.BooleanField(default=False)
    info = models.TextField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    background_color = models.CharField(max_length=20, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(null=True, blank=True, upload_to="storefronts/")
    plan = models.ForeignKey(
        SupplierPlan, null=True, on_delete=models.SET_NULL, related_name="suppliers"
    )

    objects = SupplierGroupManager()
    subclasses = InheritanceManager()

    def save(self, *args, **kwargs):
        if not self.plan:
            self.plan = SupplierPlan.objects.get_or_create_default()
        super().save(*args, **kwargs)

    def coordinates(self):
        return [self.business_address.lat, self.business_address.lng]

    def get_employees(self):
        return (
            self.employees.select_related("user")
            .filter(publish=True)
            .values(
                "pk",
                "title",
                "avatar",
                "admin",
                "owner",
                "user__full_name",
                "user__email",
            )
        )

    def create_demo_employees(self):
        from Profiles.models import BaseProfile

        user = create_user(is_supplier=True)
        admin = random.choice([True, False])
        employee = BaseProfile.objects.create_profile(
            user=user[0], company=self, company_admin=admin
        )
        return employee

    @classmethod
    def create_demo_supplier_company(cls, user, address):
        fake = Faker()
        u_phone = fake.phone_number()
        u_phone = u_phone[:25] if len(u_phone) > 25 else u_phone
        ret_com_text = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
        ret_com_name = fake.company() + " demo"
        try:
            company: SupplierCompany = SupplierCompany.objects.create_group(
                user=user,
                business_address=address,
                phone_number=u_phone,
                name=ret_com_name,
                info=ret_com_text,
            )
            for _ in range(random.randint(1, 3)):
                company.create_demo_employees(company)
            return company
        except IntegrityError:
            cls.create_demo_supplier_company(user, address)
