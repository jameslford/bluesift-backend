from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from Addresses.models import Address
from Products.models import Product
from Plans.models import CustomerPlan


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='customer_profile'
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
        blank=True,
        on_delete=models.SET_NULL,
        related_name='projects'
        )
    nickname = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nickname

    def clean(self):
        projects_allowed = self.owner.plan.project_theshhold if self.owner.plan else 10
        existing_projects = self.owner.projects.all().count()
        if existing_projects <= projects_allowed:
            return super().clean()
        else:
            raise ValidationError("Already at plan's project quota")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save()
        if not self.nickname:
            count = self.owner.projects.count() + 1
            self.nickname = 'Project ' + str(count)
        return super().save(*args, **kwargs)


class CustomerProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customer_products')
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ('product', 'project')


class CustomerProjectApplication(models.Model):
    label = models.CharField(max_length=100, blank=True, null=True)
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE, related_name='applications')
    products = models.ManyToManyField(CustomerProduct)

    def __str__(self):
        return self.label

    class Meta:
        unique_together = ('label', 'project')
