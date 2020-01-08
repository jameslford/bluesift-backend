''' profiles.urls.py '''
from django.urls import path
from .views import all_projects, dashboard, tasks


urlpatterns = [
    path('list', all_projects),
    path('dashboard/<int:project_pk>', dashboard),
    path('dashboard', dashboard),
    # path('palette/<int:project_pk>', assignments),
    # path('palette/<int:project_pk>/<int:assignment_pk>', assignments),
    path('tasks/<int:project_pk>', tasks),
    path('tasks/<int:project_pk>/<int:task_pk>', tasks),
    # path('collaborators', collaborators),
    # path('short_collabs', short_collabs)
]