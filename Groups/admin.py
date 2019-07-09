from django.contrib import admin
from .models import Company, ProCompany, RetailerCompany, ServiceType

admin.site.register(ProCompany)
admin.site.register(Company)
admin.site.register(RetailerCompany)
admin.site.register(ServiceType)

# Register your models here.
