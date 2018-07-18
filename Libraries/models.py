# Libraries.models.py

from django.db import models
from django.conf import settings
from Products.models import Product, SupplierProduct


class UserLibrary(models.Model):
    products    = models.ManyToManyField(Product)
    owner       = models.OneToOneField(
                                        settings.AUTH_USER_MODEL, 
                                        on_delete=models.CASCADE, 
                                        null=True, 
                                        related_name='user_library'
                                        )
    name        = models.CharField(max_length=50, default='Library')
    
    def __str__(self):
        return self.name

class SupplierLibrary(models.Model):
    products    = models.ManyToManyField(SupplierProduct)
    owner       = models.OneToOneField(
                                        settings.AUTH_USER_MODEL, 
                                        on_delete=models.CASCADE, 
                                        null=True,
                                        related_name='supplier_library'
                                        )
    name        = models.CharField(max_length=50, default='Library')
    
    def __str__(self):
        return self.name


    
   



