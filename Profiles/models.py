from django.db import models
from Accounts.models import User
from .choices import states

class Address(models.Model):
    address_line_1  = models.CharField(max_length=120)
    address_line_2  = models.CharField(max_length=120, null=True, blank=True)
    city            = models.CharField(max_length=120)
    country         = models.CharField(max_length=120, default='United States of America')
    state           = models.CharField(max_length=120, choices=states)
    postal_code     = models.CharField(max_length=120)



class CompanyAccount(models.Model):
    name            = models.CharField(max_length=120)
    account_owner   = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, limit_choices_to={'is_supplier' : True})
    headquarters    = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    account_users   = models.ForeignKey(User, null=True, on_delete=models.SET_NULL )



class ShippingLocation(models.Model):
    company_account     = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name='shipping_locations')
    address             = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    nickname            = models.CharField(max_length=120, null=True, blank=True)
    location_mangager   = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def limit_manager_choices(self):
        pass



    
    