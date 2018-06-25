# Product.admin.py

from django.contrib import admin

from .models import Manufacturer, Product, SupplierProduct

admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(SupplierProduct)
