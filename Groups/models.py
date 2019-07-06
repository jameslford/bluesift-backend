from model_utils.managers import InheritanceManager
from django.db import models
from Addresses.models import Address
from Plans.models import SupplierPlan


class BaseGroup(models.Model):

    subclasses = InheritanceManager()



class Company(BaseGroup):
    name = models.CharField(max_length=40, unique=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    business_address = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)
    plan = models.ForeignKey(SupplierPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')
    email_verified = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_employees(self):
        # pylint: disable=no-member
        return self.employees

    def shipping_location_count(self):
        try:
            count = self.shipping_locations.count()
            return count
        except:
            return 0



class Library(BaseGroup):
    pass