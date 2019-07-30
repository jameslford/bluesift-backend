from django.urls import path
from .views import get_library, add_project

urlpatterns = [
    path('library', get_library),
    path('add-project', add_project)
]
