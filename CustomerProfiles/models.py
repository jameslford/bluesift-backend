from django.db import models
from django.conf import settings
from Addresses.models import Address
from Products.models import Product
from Plans.models import CustomerPlan


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='user_profile'
        )
    addresses = models.ManyToManyField(Address, related_name='addresses')
    phone_number = models.IntegerField(null=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    plan = models.ForeignKey(CustomerPlan, null=True, on_delete=models.SET_NULL, related_name='customers')

    def __str__(self):
        return self.user.get_first_name() + "'s library"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.user.get_first_name() + "'s library"
        super(CustomerProfile, self).save(*args, **kwargs)


class CustomerProject(models.Model):
    owner = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='projects'
        )
    address = models.ForeignKey(
        Address,
        null=True,
        on_delete=models.SET_NULL,
        related_name='projects'
        )
    nickname = models.CharField(max_length=50)

    def __str__(self):
        if self.nickname:
            return self.nickname
        return self.owner.user.get_first_name()


class CustomerProduct(models.Model):
    use = models.CharField(max_length=100, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customer_products')
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.product.name
