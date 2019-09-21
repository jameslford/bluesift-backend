from django.urls import path
from .views import tasks, product_assignments, collaborators

urlpatterns = [
    path('tasks/<int:project_pk>', tasks),
    path('assignments/<int:project_pk>', product_assignments),
    path('collaborators/<int:project_pk>', collaborators)
]
