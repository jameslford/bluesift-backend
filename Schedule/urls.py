from django.urls import path
from .views import (
    tasks,
    product_assignments,
    collabsForService,
    collaborators,
    assignment_cud
    )

urlpatterns = [
    path('tasks/<int:project_pk>', tasks),
    path('tasks/<int:project_pk>/<int:task_pk>', tasks),
    path('assignments/<int:project_pk>', product_assignments),
    path('collaborators/<int:project_pk>', collaborators),
    path('service_collabs/<int:service_pk>', collabsForService),
    path('assignment/<int:project_pk>', assignment_cud),
    path('assignment/<int:project_pk>/<int:assignment_pk>', assignment_cud),
]
