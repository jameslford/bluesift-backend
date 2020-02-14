# Product.admin.py
from django.contrib import admin

from .models import Manufacturer, Product

admin.site.register(Manufacturer)
# admin.site.register(Product)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_filter = ('manufacturer',)
