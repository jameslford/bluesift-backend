# Product.admin.py
from django.contrib import admin

from .models import Manufacturer, Product

admin.site.register(Manufacturer)
admin.site.register(Product)
# admin.site.register(Material)
# admin.site.register(Look)
# admin.site.register(Finish)
# admin.site.register(Image)
# admin.site.register(SubMaterial)
# admin.site.register(ShadeVariation)
