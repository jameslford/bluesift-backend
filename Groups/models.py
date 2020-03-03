from django.db import models
from model_utils.managers import InheritanceManager
from Addresses.models import Address
from Plans.models import SupplierPlan


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


    def edit_group(self, user, **kwargs):
        if not user.is_supplier:
            return
        profile = user.get_profile()
        if not (profile.owner or profile.admin):
            return
        company = user.get_group()
        name = kwargs.get('name')


class SupplierCompany(models.Model):
    name = models.CharField(max_length=40, unique=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    business_address = models.OneToOneField(Address, null=True, on_delete=models.SET_NULL)
    email_verified = models.BooleanField(default=False)
    info = models.TextField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(null=True, blank=True, upload_to='storefronts/')
    plan = models.ForeignKey(SupplierPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')

    objects = SupplierGroupManager()
    subclasses = InheritanceManager()


    def save(self, *args, **kwargs):
        if not self.plan:
            self.plan = SupplierPlan.objects.get_or_create_default()
        super().save(*args, **kwargs)

    def coordinates(self):
        return [
            self.business_address.lat,
            self.business_address.lng
            ]

    def get_employees(self):
        return self.employees.select_related('user').filter(publish=True).values(
            'pk',
            'title',
            'avatar',
            'admin',
            'owner',
            'user__full_name',
            'user__email'
            )

