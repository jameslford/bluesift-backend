# Libraries.admin.py

from django.contrib import admin
from .models import UserLibrary, SupplierLibrary

admin.site.register(UserLibrary)
admin.site.register(SupplierLibrary)

# Register your models here.
