from django.urls import path
from .views import create_supplier, create_user, activate, get_token, user_details


urlpatterns = [
    path('registerUser/', create_user),
    path('registerSupplier/', create_supplier),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('get_token/', get_token),
    path('user_details/', user_details)
]
