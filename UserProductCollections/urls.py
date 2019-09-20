from django.urls import path
from .views import (
    get_library,
    crud_project,
    crud_location,
    project_detail,
    location_detail
    )

urlpatterns = [
    path('library', get_library),
    path('project', crud_project),
    path('project/<int:project_pk>', crud_project),
    path('location', crud_location),
    path('location/<int:location_pk>', crud_location),
    path('project-detail/<int:project_pk>', project_detail),
    path('location-detail/<int:pk>', location_detail)
]
