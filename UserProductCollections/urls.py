from django.urls import path
from .views import get_library

urlpatterns = [
    path('library', get_library)
]
