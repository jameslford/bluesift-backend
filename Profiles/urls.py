""" profiles.urls.py """
from django.urls import path
from .views import (
    profile_crud,
    palette,
    collaborators,
    supplier_view_employees,
    user_view_employees,
)


urlpatterns = [
    path("", profile_crud),
    path("collaborators", collaborators),
    path("collaborators/<int:pk>", collaborators),
    path("palette", palette),
    path("supplier-employees", supplier_view_employees),
    path("supplier-employees/<int:employee_pk>", supplier_view_employees),
    path("employees", user_view_employees),
    path("employees/<int:pk>", user_view_employees),
]
