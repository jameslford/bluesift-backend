from model_utils.managers import InheritanceManager
from django.db import models
from Addresses.models import Address
from Plans.models import RetailerPlan, ProPlan


class CompanyManager(models.Manager):

    def create_company(self, user, **kwargs):
        if user.is_pro:
            return ProCompany.objects.get_or_create(**kwargs)[0]
        if user.is_supplier:
            del kwargs['service']
            return RetailerCompany.objects.get_or_create(**kwargs)[0]
        raise ValueError('user is not pro or supplier')

    def delete_company(self, user):
        if not (user.is_supplier or user.is_pro):
            return
        profile = user.get_profile()
        if profile.owner:
            group = user.get_group()
            group.delete()
        return

    def edit_company(self, user, **kwargs):
        if not (user.is_pro or user.is_supplier):
            return
        profile = user.get_profile()
        if not (profile.owner or profile.admin):
            return
        company = user.get_group()
        name = kwargs.get('name')





class Company(models.Model):
    name = models.CharField(max_length=40, unique=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    business_address = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    email_verified = models.BooleanField(default=False)
    info = models.TextField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)

    objects = CompanyManager()
    subclasses = InheritanceManager()

    def __str__(self):
        return self.name

    def get_employees(self):
        # pylint: disable=no-member
        return self.employees

    def company_name(self):
        return self.name

    def nickname(self):
        return self.name

    def address(self):
        return self.business_address


class RetailerCompany(Company):
    plan = models.ForeignKey(RetailerPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')

    def get_employees(self):
        return self.employees.select_related('user').all()


class ServiceType(models.Model):
    label = models.CharField(max_length=40)


class ProCompany(Company):
    service = models.ForeignKey(ServiceType, null=True, on_delete=models.SET_NULL)
    plan = models.ForeignKey(ProPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')

    def service_type(self):
        if self.service:
            return self.service.label
        return None
