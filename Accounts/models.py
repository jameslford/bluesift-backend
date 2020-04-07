"""
Accounts.models.py
"""

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework.authtoken.models import Token
from Profiles.models import BaseProfile
from config.models import LibraryLink


class UserManager(BaseUserManager):

    def create_user(self, email: str, password: str, **kwargs):
        if not email:
            raise ValueError("User must have an email address")
        if '@' not in email:
            raise ValueError("User must have valid email address")
        if not password:
            raise ValueError("Users must have a password")

        is_supplier = kwargs.get('is_supplier', False)


        user: User = self.model.objects.create(email=email)
        user.set_password(password)
        user.full_name = kwargs.get('full_name', None)
        user.staff = kwargs.get('is_staff', False)
        user.admin = kwargs.get('is_admin', False)
        user.demo = kwargs.get('demo', False)
        user.email_verified = kwargs.get('email_verified', False)
        user.is_active = kwargs.get('is_active', False)
        user.is_supplier = is_supplier
        user.save(using=self.db)
        Token.objects.get_or_create(user=user)
        if not user.is_supplier:
            from Profiles.models import ConsumerProfile
            ConsumerProfile.objects.create(user=user)
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
    is_supplier = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    demo = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def serialize(self):
        from .serializers import user_serializer
        return user_serializer(self)

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
        if self.is_supplier:
            return profile.company
        return profile

    def get_collections(self, *select_related):
        group = self.get_group()
        if self.is_supplier:
            from Suppliers.models import SupplierLocation
            if select_related:
                return SupplierLocation.objects.prefetch_related(
                    'products'
                ).select_related(*select_related).filter(company=group)
            return SupplierLocation.objects.prefetch_related(
                'products'
            ).filter(company=group)
        from Projects.models import Project
        return Project.objects.filter(owner=group)


    def get_user_product_type(self):
        if self.is_supplier:
            from Suppliers.models import SupplierProduct
            return SupplierProduct
        from Profiles.models import LibraryProduct
        return LibraryProduct

    def get_library_links(self):
        if self.is_supplier:
            term = {'for_supplier': True}
        elif self.admin:
            term = {'for_admin': True}
        else:
            term = {'for_user': True}
        return [link for link in LibraryLink.objects.filter(**term)]
        # return [link.custom_serialize() for link in LibraryLink.objects.filter(**term)]

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    #pylint: disable=unused-argument
    def has_perm(self, perm, obj=None):
        return True

    #pylint: disable=unused-argument
    def has_module_perms(self, app_label):
        return True
