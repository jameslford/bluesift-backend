from django.urls import path
from .views import check_address, add_address, get_zipcode, set_zipcode

urlpatterns = [
    path("check-address", check_address),
    path("add-address", add_address),
    path("get-zip", get_zipcode),
    path("set-zip/<str:zipcode>", set_zipcode),
]
