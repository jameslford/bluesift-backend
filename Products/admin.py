# Product.admin.py

from django.contrib import admin

from .models import Manufacturer, Product, SupplierProduct, ProductType, Application

admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(SupplierProduct)
admin.site.register(ProductType)
admin.site.register(Application)
