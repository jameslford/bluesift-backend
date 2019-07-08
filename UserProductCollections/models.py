from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from Addresses.models import Address
from Groups.models import ProCompany, RetailerCompany
from Profiles.models import ConsumerProfile, RetailerEmployeeProfile, ProEmployeeProfile
from model_utils.managers import InheritanceManager


class RetailerLocation(models.Model):
    nickname = models.CharField(max_length=60)
    company = models.ForeignKey(
        RetailerCompany,
        on_delete=models.CASCADE,
        related_name='shipping_locations'
        )
    local_admin = models.ForeignKey(
        RetailerEmployeeProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        )
    address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='retailer_locations'
    )
    approved_in_store_seller = models.BooleanField(default=False)
    approved_online_seller = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    info = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(max_length=300, blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='storefronts/')
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return str(self.company) + ' ' + str(self.number)

    def average_rating(self):
        avg_rating = self.ratings.all().aggregate(models.Avg('rating'))
        avg_rating = avg_rating.get('rating_avg', None)
        return avg_rating

    def rating_count(self):
        return self.ratings.all().count()

    def location_manager(self):
        if self.local_admin:
            return [self.local_admin.id, self.local_admin.user.get_first_name()]
        sys_admin = self.company.employees.filter(company_account_admin=True).first()
        if sys_admin:
            return [sys_admin.id, sys_admin.user.get_first_name()]
        owner = self.company.employees.filter(company_account_owner=True).first()
        return [owner.id, owner.user.get_first_name()]

    def assign_number(self):
        num_list = []
        num = None
        all_locations = self.company.shipping_locations.all()
        for loc in all_locations:
            if loc.number:
                num_list.append(loc.number)
            else:
                num_list.append(0)
        if num_list:
            num = max(set(num_list)) + 1
        else:
            num = 1
        return num

    def product_count(self):
        return self.priced_products.count()

    def address_string(self):
        if self.address:
            return self.address.address_string()
        return 'No Address'

    def company_name(self):
        return self.company.name

    def clean(self):
        # makes sure employee assigned to local_admin is a company employee
        if not self.local_admin:
            return super().clean()
        if self.local_admin.company == self.company:
            return super().clean()
        raise ValidationError('Employee not a company employee')

    def save(self, *args, **kwargs):
        if not self.address:
            self.approved_in_store_seller = False
            self.approved_online_seller = False
        if not self.number:
            self.number = self.assign_number()
        if not self.nickname:
            self.nickname = self.company.name + ' ' + str(self.number)
        self.full_clean()
        super(RetailerLocation, self).save(*args, **kwargs)


class BaseProject(models.Model):
    pro_collaborator = models.ManyToManyField(ProEmployeeProfile)
    collaborators = models.ManyToManyField(ConsumerProfile)
    deadline = models.DateTimeField(null=True, blank=True)
    template = models.BooleanField(default=False)
    address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='projects'
    )

    objects = models.Manager()
    subclasses = InheritanceManager()

    def product_count(self):
        return self.products.count()

    def application_count(self):
        # pylint: disable=no-member
        if self.applications:
            return self.applications.count()
        return 0


class ProProject(BaseProject):
    nickname = models.CharField(max_length=60)
    owner = models.ForeignKey(
        ProCompany,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    class Meta:
        unique_together = ('nickname', 'owner')

    def save(self, *args, **kwargs):
        if not self.nickname:
            count = self.owner.projects.count() + 1
            self.nickname = 'Project ' + str(count)
        self.full_clean()
        return super().save(*args, **kwargs)


class ConsumerProject(BaseProject):
    nickname = models.CharField(max_length=60)
    owner = models.ForeignKey(
        ConsumerProfile,
        on_delete=models.CASCADE,
        related_name='projects'
        )

    class Meta:
        unique_together = ('nickname', 'owner')

    def __str__(self):
        return self.nickname

    def clean(self):
        # pylint: disable=no-member
        projects_allowed = self.owner.plan.project_theshhold if self.owner.plan else 10
        existing_projects = self.owner.projects.all().count()
        if existing_projects <= projects_allowed:
            return super().clean()
        raise ValidationError("Already at plan's project quota")

    def save(self, *args, **kwargs):
        if not self.nickname:
            count = self.owner.projects.count() + 1
            self.nickname = 'Project ' + str(count)
        self.full_clean()
        return super().save(*args, **kwargs)
