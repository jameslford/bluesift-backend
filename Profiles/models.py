from django.db import models
from Accounts.models import User
from Addresses.models import Address



class CompanyAccount(models.Model):
    name                = models.CharField(max_length=120)
    account_owner       = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, limit_choices_to={'is_supplier' : True})
    headquarters        = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name



class CompanyShippingLocation(models.Model):
    company_account     = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name='shipping_locations')
    address             = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    nickname            = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        if self.nickname:
            return self.nickname
        else:
            return self.address


class CustomerProfile(models.Model):
    shipping_address    = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='shipping_address')
    addresses           = models.ManyToManyField(Address, related_name='addresses')

    def __str__(self):
        return self.shipping_address
    