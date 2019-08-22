from django.urls import path
from .views import create_user, activate, custom_login, get_user


urlpatterns = [
    path('get-user', get_user),
    path('register-user/', create_user),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('login/', custom_login),
]
