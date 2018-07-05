# Accounts.models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from Plans.models import Plan




class UserManager(BaseUserManager):
      
    def create_user(self, email, first_name=None, 
                        last_name=None, password=None, 
                        is_active=True, is_staff=False, 
                        is_admin=False, plan=None, 
                        confirmed=False, is_supplier=False):
        if not email:
            raise ValueError("User must have an email address")
        if not password:
            raise ValueError("Users must have a password")
        user_obj = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.is_supplier = is_supplier
        user_obj.plan = plan
        user_obj.save(using=self.db)
        return user_obj

    def create_staffuser(self, email, first_name=None, last_name=None, password=None):

        user = self.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=True,
            is_staff=True
        )
        return user

    def create_superuser(self, email, first_name=None, last_name=None, password=None):

        user = self.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_staff=True,
            is_admin=True,
            is_active=True  
        )
        return user

  
        



class User(AbstractBaseUser):

    email               = models.EmailField(max_length=200, unique=True)
    first_name          = models.CharField(max_length=50, help_text='First Name', null=True, blank=True)
    last_name           = models.CharField(max_length=50, help_text='Last Name', null=True, blank=True)
    plan                = models.ForeignKey(Plan,null=True, blank=True, on_delete=models.SET_NULL)
    is_supplier         = models.BooleanField(default=False)
    date_registered     = models.DateTimeField(auto_now_add=True, null=True)
    date_confirmed      = models.DateTimeField(auto_now_add=True, null=True)
    

    is_active           = models.BooleanField(default=False)
    staff               = models.BooleanField(default=False)
    admin               = models.BooleanField(default=False)
   
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_first_name(self):
        if self.first_name:
            return self.first_name
        return self.email

    def get_last_name(self):
        if self.last_name:
            return self.last_name
        
    def get_fullname(self):
        if self.first_name and self.last_name:
            return self.first_name + self.last_name

    def get_short_name(self):
        return self.email

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
