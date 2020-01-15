from django.contrib import admin
from .models import (
    SupplierEmployeeProfile,
    ConsumerProfile
    )


admin.site.register(ConsumerProfile)
admin.site.register(SupplierEmployeeProfile)

# Register your models here.
