from django.urls import path
from .views import check_address, add_address

urlpatterns = [
    path('check-address', check_address),
    path('add-address', add_address)
]
