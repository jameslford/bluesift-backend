''' profiles.urls.py '''
from django.urls import path
from .views import all_projects, dashboard, get_tasks, resources


urlpatterns = [
    path('list', all_projects),
    path('<int:project_pk>', dashboard),
    path('', dashboard),
    path('tasks/<int:project_pk>', get_tasks),
    path('tasks/<int:project_pk>/<int:task_pk>', get_tasks),
    path('resources/<int:project_pk>', resources),
    path('resources/<int:project_pk>/<int:product_pk>', resources)
]