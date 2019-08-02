from django.urls import path
from .views import get_library, crud_project

urlpatterns = [
    path('library', get_library),
    path('project', crud_project),
    path('project/<int:project_pk>', crud_project),
]
