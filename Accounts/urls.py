from django.urls import path
from .views import create_user, activate, custom_login


urlpatterns = [
    path('registerUser/', create_user),
    # path('registerSupplier/', create_supplier),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('login/', custom_login),
    # path('user_details/', user_details)
]
