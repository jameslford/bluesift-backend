from django.contrib import admin
from django.contrib.postgres import fields
from ProductFilter.models import ProductFilter, QueryIndex

# Register your models here.

admin.site.register(ProductFilter)
admin.site.register(QueryIndex)
