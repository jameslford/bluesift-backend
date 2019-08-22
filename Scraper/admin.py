from django.contrib import admin
from .models import (
    ScraperBaseProduct,
    ScraperCategory,
    ScraperDepartment,
    ScraperSubgroup,
    ScraperManufacturer
)

admin.site.register(ScraperSubgroup)
admin.site.register(ScraperManufacturer)
admin.site.register(ScraperDepartment)
admin.site.register(ScraperCategory)
