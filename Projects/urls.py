''' profiles.urls.py '''
from django.urls import path
from .views import all_projects, dashboard, tasks, resources


urlpatterns = [
    path('list', all_projects),
    path('dashboard/<int:project_pk>', dashboard),
    path('dashboard', dashboard),
    path('tasks/<int:project_pk>', tasks),
    path('tasks/<int:project_pk>/<int:task_pk>', tasks),
    path('resources/<int:pk>', resources)
]