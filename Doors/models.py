from django.db import models
from Products.models import ProductSubClass

class Door(ProductSubClass):
    name = models.CharField(max_length=10)
