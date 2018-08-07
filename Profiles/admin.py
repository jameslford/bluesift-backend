from django.contrib import admin
from .models import CompanyAccount, CompanyShippingLocation, CustomerProfile, CustomerProject


admin.site.register(CompanyAccount)
admin.site.register(CompanyShippingLocation)
admin.site.register(CustomerProfile)
admin.site.register(CustomerProject)
# Register your models here.
