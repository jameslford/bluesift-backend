# Product.admin.py

from django.contrib import admin

from .models import Manufacturer, Product, SupplierProduct, ProductType, Application

class ProductTypeAdmin(admin.ModelAdmin):
    model = ProductType
    fields = ('material', 'unit', 'id', )

admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(SupplierProduct)
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Application)
