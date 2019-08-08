from model_utils.managers import InheritanceManager
from django.db import models
from django.conf import settings
from Groups.models import ProCompany, RetailerCompany
from Plans.models import ConsumerPlan


class ProfileManager(models.Manager):
    def create_profile(self, user, **kwargs):
        if user.is_supplier or user.is_pro:
            company = kwargs.get('company', None)
            owner = kwargs.get('owner', False)
            admin = kwargs.get('admin', False)
            title = kwargs.get('title', None)
            if not company:
                raise ValueError('must provide company')
            if user.is_pro:
                return ProEmployeeProfile.objects.get_or_create(
                    user=user,
                    company=company,
                    owner=owner,
                    title=title,
                    admin=admin)[0]
            return RetailerEmployeeProfile.objects.get_or_create(
                user=user,
                company=company,
                owner=owner,
                title=title,
                admin=admin)[0]
        plan = kwargs.get('plan', None)
        phone = kwargs.get('phone_number', None)
        return ConsumerProfile.objects.get_or_create(
            user=user,
            plan=plan,
            phone_number=phone)[0]
        # profile.save(using=self.db)


class BaseProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='profile'
        )
    objects = ProfileManager()
    subclasses = InheritanceManager()

    def name(self):
        return self.user.get_full_name()


class ConsumerProfile(BaseProfile):
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    plan = models.ForeignKey(
        ConsumerPlan,
        null=True,
        on_delete=models.SET_NULL,
        related_name='customers')

    def __str__(self):
        return self.user.get_first_name() + "'s library"

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        if self.user.is_pro or self.user.is_supplier:
            raise ValueError('user should not be pro or supplier')
        super(ConsumerProfile, self).save(*args, **kwargs)


class EmployeeBaseProfile(BaseProfile):
    """
    shared fields for pro-employees and retailer-employees

    owners can delete/edit company objects

    owners and admins can add, delete, and edit projects/retailer locations
    """
    owner = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    title = models.CharField(max_length=100, null=True)

    class Meta:
        abstract = True


class ProEmployeeProfile(EmployeeBaseProfile):
    company = models.ForeignKey(
        ProCompany,
        on_delete=models.CASCADE,
        related_name='employees'
        )

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        if not self.user.is_pro:
            raise ValueError('user is not pro')
        owner_count = self.company.employees.filter(owner=True).count()
        if owner_count > 0:
            raise ValueError(f'{self.company.name} already has an owner - cannot have more than 1')
        super(ProEmployeeProfile, self).save(*args, **kwargs)


class RetailerEmployeeProfile(EmployeeBaseProfile):
    company = models.ForeignKey(
        RetailerCompany,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    def __str__(self):
        return self.user.get_full_name()

    def locations_managed(self):
        return [location.pk for location in self.managed_locations.all()]

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        if not self.user.is_supplier:
            raise ValueError('user is not retailer')
            # pylint: disable=no-member
        owner_count = self.company.employees.all().filter(owner=True).count()
        if owner_count > 0:
            raise ValueError(f'{self.company.name} already has an owner - cannot have more than 1')
        super(RetailerEmployeeProfile, self).save(*args, **kwargs)

    # def __str__(self):
    #     return self.user.email

    # def get_plan(self):
    #     plan = company.plan

    # def clean(self):
    #     # makes sure company owners/admins do not exceed quota
    #     # hardcoding quota for now, but leaves door open
    #     owners_allowed = 1
    #     admins_allowed = 1
    #     if self.admin:
    #         existing_admins = self.company.employees.filter(company_account_admin=True).count()
    #         if existing_admins >= admins_allowed:
    #             raise ValidationError('Maximum admins, ' + str(admins_allowed) + ' already exist')
    #     if self.owner:
    #         existing_owners = self.company.employees.filter(company_account_owner=True).count()
    #         if existing_owners >= owners_allowed:
    #             raise ValidationError('Maximum owners, ' + str(owners_allowed) + ' already exist')
    #     return super().clean()

    # def save(self, *args, **kwargs):
    #     # calling full_clean() which executes clean() above
    #     # among 2 other default methods
    #     self.full_clean()
    #     if not (self.user.is_pro or self.user.is_supplier):
    #         raise ValidationError('User is not pro or supplier')
    #     super(EmployeeProfile, self).save(*args, **kwargs)

    # def name(self):
    #     return self.user.get_first_name()

    # def email(self):
    #     return self.user.email
