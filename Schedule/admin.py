from django.contrib import admin
from .models import ProductAssignment, ProjectTask, ProCollaborator, ConsumerCollaborator


admin.site.register(ProductAssignment)
admin.site.register(ProjectTask)
admin.site.register(ProCollaborator)
admin.site.register(ConsumerCollaborator)
