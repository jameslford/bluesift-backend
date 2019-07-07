# Accounts.models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework.authtoken.models import Token
from Profiles.models import BaseProfile


class UserManager(BaseUserManager):

    def create_user(
            self,
            email,
            full_name=None,
            password=None,
            is_active=True,
            is_staff=False,
            is_admin=False,
            is_supplier=False,
            is_pro=False
            ):
        if not email:
            raise ValueError("User must have an email address")
        if '@' not in email:
            raise ValueError("User must have valid email address")
        if not password:
            raise ValueError("Users must have a password")
        if is_supplier and is_pro:
            raise ValueError('User cannot be proffesional and supplier')
        user_obj = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
        )

        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.is_supplier = is_supplier
        user_obj.save(using=self.db)
        Token.objects.get_or_create(user=user_obj)
        return user_obj

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

    def get_short_name(self):
        return self.email

    def get_token(self):
        # pylint: disable=no-member
        return self.token

    def get_profile(self):
        return BaseProfile.subclasses.get_subclass(user=self)

    def get_group(self):
        profile = self.get_profile()
        if self.is_supplier or self.is_pro:
            return profile.company
        return profile.library

    def get_collections(self):
        from UserProductCollections.models import RetailerLocation, ProProject, ConsumerProject
        group = self.get_group()
        if self.is_supplier:
            return RetailerLocation.objects.select_related(
                'product',
            ).filter(company=group)
        if self.is_pro:
            return ProProject.objects.select_related(
                'product'
            ).filter(owner=group)
        return ConsumerProject.objects.select_related(
            'product'
        ).filter(owner=group)

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
