from django.contrib import admin
from .models import (
    ProEmployeeProfile,
    RetailerEmployeeProfile,
    ConsumerProfile
    )


admin.site.register(ConsumerProfile)
admin.site.register(RetailerEmployeeProfile)
admin.site.register(ProEmployeeProfile)

# Register your models here.
