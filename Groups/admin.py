from django.contrib import admin
from .models import ProCompany, RetailerCompany, ServiceType

admin.site.register(ProCompany)
admin.site.register(RetailerCompany)
admin.site.register(ServiceType)

# Register your models here.
