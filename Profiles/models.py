from django.db import models
from django.conf import settings
from Addresses.models import Address



class CompanyAccount(models.Model):
    name                = models.CharField(max_length=120)
    account_owner       = models.ForeignKey(
                                            settings.AUTH_USER_MODEL,
                                            null=True,
                                            on_delete=models.CASCADE,
                                            limit_choices_to={'is_supplier' : True},
                                            related_name='company_account'
                                            )
    headquarters        = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    phone_number        = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name



class CompanyShippingLocation(models.Model):
    company_account     = models.ForeignKey(
                                            CompanyAccount, 
                                            on_delete=models.CASCADE, 
                                            related_name='shipping_locations'
                                            )
    address             = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)
    nickname            = models.CharField(max_length=120, null=True, blank=True)
    approved_seller     = models.BooleanField(default=False)

    def __str__(self):
        if self.nickname:
            return self.nickname
        else:
            return self.address


class CustomerProfile(models.Model):
    user                = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='user_profile')
    shipping_address    = models.ForeignKey(Address, null=True, on_delete=models.CASCADE, related_name='shipping_address')
    addresses           = models.ManyToManyField(Address, related_name='addresses')
    phone_number        = models.IntegerField(null=True)

    def __str__(self):
        return self.shipping_address
    