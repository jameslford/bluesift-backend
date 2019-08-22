from django.urls import path
from .views import get_library, crud_project, crud_location

urlpatterns = [
    path('library', get_library),
    path('project', crud_project),
    path('project/<int:project_pk>', crud_project),
    path('location', crud_location),
    path('location/<int:location_pk>', crud_location)
]
