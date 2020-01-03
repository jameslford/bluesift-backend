from django.contrib import admin
from .models import ProductAssignment, ProjectTask, ConsumerProject, ProProject


admin.site.register(ProductAssignment)
admin.site.register(ProjectTask)
admin.site.register(ConsumerProject)
admin.site.register(ProProject)