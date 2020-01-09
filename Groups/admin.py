from django.contrib import admin
from .models import ProCompany, RetailerCompany, ServiceType, ConsumerLibrary

admin.site.register(ProCompany)
admin.site.register(RetailerCompany)
admin.site.register(ServiceType)
admin.site.register(ConsumerLibrary)

# Register your models here.
