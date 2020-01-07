''' profiles.urls.py '''
from django.urls import path
from .views import profile_crud


urlpatterns = [
    path('profile', profile_crud),
]
