from model_utils.managers import InheritanceManager
from model_utils.choices import Choices
from django.db import models
from Addresses.models import Address
from Plans.models import RetailerPlan, ProPlan


class Company(models.Model):
    name = models.CharField(max_length=40, unique=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    business_address = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_employees(self):
        # pylint: disable=no-member
        return self.employees


class RetailerCompany(Company):
    plan = models.ForeignKey(RetailerPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')


class ServiceType(models.Model):
    label = models.CharField(max_length=40)


class ProCompany(Company):
    service = models.ForeignKey(ServiceType, null=True, on_delete=models.SET_NULL)
    plan = models.ForeignKey(ProPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')
