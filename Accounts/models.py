"""
Accounts.models.py
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework.authtoken.models import Token
from Profiles.models import BaseProfile


class UserManager(BaseUserManager):

    def create_user(self, email: str, password: str, **kwargs):
        if not email:
            raise ValueError("User must have an email address")
        if '@' not in email:
            raise ValueError("User must have valid email address")
        if not password:
            raise ValueError("Users must have a password")

        is_supplier = kwargs.get('is_supplier', False)
        is_pro = kwargs.get('is_pro', False)
        if is_supplier and is_pro:
            raise ValueError('User cannot be proffesional and supplier')

        user = self.model.objects.create(email=email)
        user.set_password(password)
        user.full_name = kwargs.get('full_name', None)
        user.staff = kwargs.get('is_staff', False)
        user.admin = kwargs.get('is_admin', False)
        user.is_active = kwargs.get('is_active', False)
        user.is_supplier = is_supplier
        user.is_pro = is_pro
        user.save(using=self.db)
        Token.objects.get_or_create(user=user)
        return user

    def create_staffuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_active=True,
            is_staff=True
        )
        return user

    def create_superuser(self, email, full_name=None, password=None):

        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_staff=True,
            is_admin=True,
            is_active=True
            )
        return user


class User(AbstractBaseUser):

    email = models.EmailField(max_length=200, unique=True)
    full_name = models.CharField(max_length=50, help_text='First Name', null=True, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True, null=True)
    date_confirmed = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=False)
    is_pro = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_first_name(self):
        if self.full_name:
            first_name = self.full_name.split(' ')[0]
            return first_name
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def get_initials(self):
        full_name = self.get_full_name()
        inits = [word[0].upper() for word in full_name.split()]
        return ''.join(inits)

    def get_token(self):
        # pylint: disable=no-member
        return self.token

    def get_profile(self):
        return BaseProfile.subclasses.filter(user=self).select_subclasses().first()

    def get_group(self):
        profile = self.get_profile()
        if self.is_supplier or self.is_pro:
            return profile.company
        return profile

    def get_collections(self):
        from UserProductCollections.models import RetailerLocation, ProProject, ConsumerProject
        group = self.get_group()
        if self.is_supplier:
            return RetailerLocation.objects.prefetch_related(
                'products'
            ).filter(company=group)
        if self.is_pro:
            return ProProject.objects.prefetch_related(
                'products'
            ).filter(owner=group)
        return ConsumerProject.objects.prefetch_related(
            'products'
        ).filter(owner=group)

    def get_user_product_type(self):
        from UserProducts.models import RetailerProduct, ProjectProduct
        if self.is_supplier:
            return RetailerProduct
        return ProjectProduct

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
