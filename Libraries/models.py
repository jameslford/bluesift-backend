# Libraries.models.py

from django.db import models
from django.conf import settings
from Products.models import Product, SupplierProduct


class Library(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default='Library')
    
    def __str__(self):
        return self.name

class UserLibrary(Library):
    products = models.ManyToManyField(Product)

class SupplierLibrary(Library):
    products = models.ManyToManyField(SupplierProduct)
    


    
   



