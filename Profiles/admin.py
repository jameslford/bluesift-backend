from django.contrib import admin
from .models import(
    CompanyAccount,
    CompanyShippingLocation,
    CustomerProfile,
    CustomerProduct,
    CustomerProject,
    SupplierProduct
    )


admin.site.register(CompanyAccount)
admin.site.register(CompanyShippingLocation)
admin.site.register(CustomerProfile)
admin.site.register(CustomerProject)
admin.site.register(SupplierProduct)
admin.site.register(CustomerProduct)

# Register your models here.
