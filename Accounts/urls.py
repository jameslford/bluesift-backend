from django.urls import path
from .views import create_user, activate, custom_login


urlpatterns = [
    path('register-user/', create_user),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('login/', custom_login),
]
