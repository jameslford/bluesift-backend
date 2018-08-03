from django.urls import path, include, re_path
from .views import user_library

urlpatterns = [
    path('mylib', user_library)
]