''' profiles.urls.py '''
from django.urls import path
from .views import profile_crud, palette


urlpatterns = [
    path('profile', profile_crud),
    path('palette', palette)
]
