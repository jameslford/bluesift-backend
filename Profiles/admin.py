from django.contrib import admin
from .models import CompanyAccount, CompanyShippingLocation, CustomerProfile


admin.site.register(CompanyAccount)
admin.site.register(CompanyShippingLocation)
admin.site.register(CustomerProfile)

# Register your models here.
