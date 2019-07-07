from model_utils.managers import InheritanceManager
from django.db import models
from django.conf import settings
from Groups.models import ProCompany, RetailerCompany
from Plans.models import ConsumerPlan
# from django.core.exceptions import ValidationError
# from Groups.models import Company, Library
# from Plans.models import CustomerPlan
# from decimal import Decimal
# from django.db.models import QuerySet
# from django.db.models import Avg
# from django.db.models.functions import Cast, Coalesce, Least
# from Products.models import Product
# from Addresses.models import Address


class ProfileManager(models.Manager):
    def create_profile(self, user, **kwargs):
        if user.is_supplier or user.is_pro:
            company = kwargs.get('company', None)
            owner = kwargs.get('owner', False)
            admin = kwargs.get('admin', False)
            if not company:
                raise ValueError('must provide company')
            if user.is_pro:
                profile = ProEmployeeProfile(
                    user=user,
                    company=company,
                    owner=owner,
                    admin=admin)
            else:
                profile = RetailerEmployeeProfile(
                    user=user,
                    company=company,
                    owner=owner,
                    admin=admin)
        else:
            plan = kwargs.get('plan', None)
            phone = kwargs.get('phone_number', None)
            profile = ConsumerProfile(
                user=user,
                plan=plan,
                phone_number=phone)
        profile.save(using=self.db)


class BaseProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        )
    objects = ProfileManager()
    subclasses = InheritanceManager()

    # def get_group(self):
    #     subclass = BaseProfile.subclasses.get_subclass(self.pk)
    # psuedo if subclass == customerprofile:
    # return subclass.library
    # else:
    # return subclass.company


class ConsumerProfile(BaseProfile):
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    plan = models.ForeignKey(
        ConsumerPlan,
        null=True,
        on_delete=models.SET_NULL,
        related_name='customers')

    def __str__(self):
        return self.user.get_first_name() + "'s library"

    def save(self, *args, **kwargs):
        if self.user.is_pro or self.user.is_supplier:
            raise ValueError('user should not be pro or supplier')
        super(ConsumerProfile, self).save(*args, **kwargs)


class EmployeeBaseProfile(BaseProfile):
    owner = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    title = models.CharField(max_length=100, null=True)

    class Meta:
        abstract = True


class ProEmployeeProfile(EmployeeBaseProfile):
    company = models.ForeignKey(
        ProCompany,
        on_delete=models.CASCADE,
        related_name='employees'
        )


class RetailerEmployeeProfile(EmployeeBaseProfile):
    company = models.ForeignKey(
        RetailerCompany,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    # def __str__(self):
    #     return self.user.email


    # def get_plan(self):
    #     plan = company.plan


    # def clean(self):
    #     # makes sure company owners/admins do not exceed quota
    #     # hardcoding quota for now, but leaves door open
    #     owners_allowed = 1
    #     admins_allowed = 1
    #     if self.admin:
    #         existing_admins = self.company.employees.filter(company_account_admin=True).count()
    #         if existing_admins >= admins_allowed:
    #             raise ValidationError('Maximum admins, ' + str(admins_allowed) + ' already exist')
    #     if self.owner:
    #         existing_owners = self.company.employees.filter(company_account_owner=True).count()
    #         if existing_owners >= owners_allowed:
    #             raise ValidationError('Maximum owners, ' + str(owners_allowed) + ' already exist')
    #     return super().clean()


    # def save(self, *args, **kwargs):
    #     # calling full_clean() which executes clean() above
    #     # among 2 other default methods
    #     self.full_clean()
    #     if not (self.user.is_pro or self.user.is_supplier):
    #         raise ValidationError('User is not pro or supplier')
    #     super(EmployeeProfile, self).save(*args, **kwargs)

    # def name(self):
    #     return self.user.get_first_name()

    # def email(self):
    #     return self.user.email
