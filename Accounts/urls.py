from django.urls import path, include, re_path
from .views import create_supplier, create_user, activate, get_token


urlpatterns = [
    path('registerUser/', create_user),
    path('registerSupplier/', create_supplier),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('get_token/', get_token),
]