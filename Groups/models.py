import datetime
from django.db import models
from model_utils.managers import InheritanceManager
from Addresses.models import Address
from Plans.models import RetailerPlan, ProPlan


class CompanyManager(models.Manager):

    def create_company(self, user, **kwargs):
        if user.is_pro:
            return ProCompany.objects.get_or_create(**kwargs)[0]
        if user.is_supplier:
            if kwargs.get('service', False):
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
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    business_address = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    email_verified = models.BooleanField(default=False)
    info = models.TextField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(null=True, blank=True, upload_to='storefronts/')

    objects = CompanyManager()
    subclasses = InheritanceManager()

    def __str__(self):
        return f'{self.name} {self.pk}'

    def get_employees(self):
        # pylint: disable=no-member
        return self.employees


    def coordinates(self):
        # coordinates = self.address.coordinates
        return [
            self.business_address.lat,
            self.business_address.lng
            ]


class RetailerCompany(Company):
    plan = models.ForeignKey(RetailerPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')

    def get_employees(self):
        return self.employees.select_related('user').all()

    def save(self, *args, **kwargs):
        if not self.plan:
            self.plan = RetailerPlan.objects.get_or_create_default()
        super().save(*args, **kwargs)

    def custom_serialize(self, full=False):
        from .serializers import BusinessSerializer
        return BusinessSerializer(self, full).getData()


class ServiceType(models.Model):
    label = models.CharField(max_length=40)
    description = models.CharField(max_length=500, blank=True, default='')
    image = models.ImageField(null=True, blank=True, upload_to='misc/')

    def custom_serialize(self):
        return {
            'label': self.label,
            'description': self.description,
            'image': self.image.url if self.image else None
            }

    def __str__(self):
        return self.label


class ProCompany(Company):
    service = models.ForeignKey(ServiceType, null=True, on_delete=models.SET_NULL)
    plan = models.ForeignKey(ProPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')

    def service_type(self):
        if self.service:
            return self.service.label
        return None

    def get_employees(self):
        return self.employees.select_related('user').all()

    def custom_serialize(self, full=False):
        from .serializers import BusinessSerializer
        return BusinessSerializer(self, full).getData()

    def save(self, *args, **kwargs):
        if not self.plan:
            self.plan = ProPlan.objects.get_or_create_default()
        super().save(*args, **kwargs)

