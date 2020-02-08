''' profiles.urls.py '''
from django.urls import path
from .views import profile_crud, palette, collaborators


urlpatterns = [
    path('', profile_crud),
    path('collaborators', collaborators),
    path('collaborators/<int:pk>', collaborators),
    path('palette', palette)
]
