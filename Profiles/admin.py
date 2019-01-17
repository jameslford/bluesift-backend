from django.contrib import admin
from .models import (
    CompanyAccount,
    CompanyShippingLocation,
    SupplierProduct
    )


admin.site.register(CompanyAccount)
admin.site.register(CompanyShippingLocation)
admin.site.register(SupplierProduct)

# Register your models here.
