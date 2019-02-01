from django.contrib import admin
from .models import (
    CompanyAccount,
    CompanyShippingLocation,
    SupplierProduct,
    EmployeeProfile
    )


admin.site.register(CompanyAccount)
admin.site.register(CompanyShippingLocation)
admin.site.register(SupplierProduct)
admin.site.register(EmployeeProfile)

# Register your models here.
