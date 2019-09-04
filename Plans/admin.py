from django.contrib import admin
from .models import ConsumerPlan, ProPlan, RetailerPlan

admin.site.register(ConsumerPlan)
admin.site.register(RetailerPlan)
admin.site.register(ProPlan)

# Register your models here.
