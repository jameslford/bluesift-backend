from django.db import models
from Addresses.models import Address
from model_utils.managers import InheritanceManager


class LocationManager(models.Manager):

    def create_location(self, **kwargs):
        pass


class BaseLocation(models.Model):
    nickname = models.CharField(max_length=120, null=True, blank=True)
    address = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)

    subclasses = InheritanceManager()


class SupplierLocation(models.Model):
    company_account = models.ForeignKey(
        CompanyAccount,
        on_delete=models.CASCADE,
        related_name='shipping_locations'
        )
    local_admin = models.ForeignKey(
        EmployeeProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
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
        return str(self.company_account) + ' ' + str(self.number)

    def average_rating(self):
        avg_rating = self.ratings.all().aggregate(models.Avg('rating'))
        avg_rating = avg_rating.get('rating_avg', None)
        return avg_rating

    def rating_count(self):
        return self.ratings.all().count()

    def location_manager(self):
        if self.local_admin:
            return [self.local_admin.id, self.local_admin.user.get_first_name()]
        sys_admin = self.company_account.employees.filter(company_account_admin=True).first()
        if sys_admin:
            return [sys_admin.id, sys_admin.user.get_first_name()]
        owner = self.company_account.employees.filter(company_account_owner=True).first()
        return [owner.id, owner.user.get_first_name()]

    def assign_number(self):
        num_list = []
        num = None
        all_locations = self.company_account.shipping_locations.all()
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
        return self.company_account.name

    def clean(self):
        # makes sure employee assigned to local_admin is a company employee
        if not self.local_admin:
            return super().clean()
        if self.local_admin.company_account == self.company_account:
            return super().clean()
        else:
            raise ValidationError('Employee not a company employee')

    def save(self, *args, **kwargs):
        if not self.address:
            self.approved_online_seller = False
        if not self.number:
            self.number = self.assign_number()
        if not self.nickname:
            self.nickname = self.company_account.name + ' ' + str(self.number)
        self.full_clean()
        super(CompanyLocation, self).save(*args, **kwargs)


class Project(models.Model):
    owner = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='projects'
        )
    deadline = models.DateTimeField(null=True, blank=True)
    template = models.BooleanField(default=False)

    def __str__(self):
        return self.nickname

    def product_count(self):
        return self.products.count()

    def application_count(self):
        # pylint: disable=no-member
        if self.applications:
            return self.applications.count()
        return 0

    def clean(self):
        # pylint: disable=no-member
        projects_allowed = self.owner.plan.project_theshhold if self.owner.plan else 10
        existing_projects = self.owner.projects.all().count()
        if existing_projects <= projects_allowed:
            return super().clean()
        raise ValidationError("Already at plan's project quota")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save()
        if not self.nickname:
            count = self.owner.projects.count() + 1
            self.nickname = 'Project ' + str(count)
        return super().save(*args, **kwargs)
