from django.db import models
from django.conf import settings
from model_utils.managers import InheritanceManager
from Groups.models import ProCompany, RetailerCompany
from Plans.models import ConsumerPlan


class ProfileManager(models.Manager):

    def create_profile(self, user, **kwargs):
        if user.is_supplier or user.is_pro:
            company = kwargs.get('company')
            company_pk = kwargs.get('company_pk')
            owner = kwargs.get('owner', False)
            admin = kwargs.get('admin', False)
            title = kwargs.get('title', None)
            if not company or company_pk:
                raise ValueError('must provide company')
            if user.is_pro:
                if not company:
                    company = ProCompany.objects.get(pk=company_pk)
                return ProEmployeeProfile.objects.get_or_create(
                    user=user,
                    company=company,
                    owner=owner,
                    title=title,
                    admin=admin)[0]
            if not company:
                company = RetailerCompany.objects.get(pk=company_pk)
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

    def update_profile(self, user, **kwargs):

        profile: BaseProfile = user.get_profile()
        profile_pk = kwargs.get('pk')
        if profile_pk and profile_pk != profile.pk:
            return self.employee_update_by_owner(user, **kwargs)

        avatar = kwargs.get('avatar')
        if avatar:
            if avatar == 'clear':
                profile.avatar = None
            else:
                try:
                    image = avatar[0]
                    profile.avatar.save(image.name, image)
                except IndexError:
                    pass

        profile.save()
        return profile

    def employee_update_by_owner(self, user, **kwargs):
        return None



class BaseProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='profile'
        )
    date_create = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='profiles/')
    objects = ProfileManager()
    subclasses = InheritanceManager()

    def name(self):
        return self.user.get_full_name()


class ConsumerProfile(BaseProfile):
    phone_number = models.CharField(max_length=30, null=True, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.user.is_pro:
            raise ValueError('user is not pro')
        # if self.owner:
        #     owner = self.company.employees.filter(owner=True).first()
        #     if owner != self:
        #         raise ValueError(f'{self.company.name} already has an owner - cannot have more than 1')
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

    def save(self, *args, **kwargs):
        if not self.user.is_supplier:
            raise ValueError('user is not retailer')
        # if self.owner:
        #     owners = self.company.employees.filter(owner=True).first()
        #     if owners != self:
        #         raise ValueError(f'{self.company.name} already has an owner - cannot have more than 1')
        super(RetailerEmployeeProfile, self).save(*args, **kwargs)



        # profile.user.name = kwargs.get('user_name', profile.user.full_name)
        # email = kwargs.get('email')
        # if email:
        #     profile.user.email = email
        #     profile.user.email_verified = False
        # user.save()


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
