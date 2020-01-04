
from django.urls import path
from .views import locations, crud_location, public_location

urlpatterns = [
    path('locations', locations),
    path('location-public/<int:pk>', public_location),
    path('location', crud_location),
    path('location/<int:pk>', crud_location)
]
