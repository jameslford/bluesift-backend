# Product.admin.py

from django.contrib import admin

from .models import Manufacturer, Product, Material, Build, Category, Look


admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(Build)
admin.site.register(Material)
admin.site.register(Look)
admin.site.register(Category)



