
from django.urls import path
from .views import locations, crud_location

urlpatterns = [
    path('locations', locations),
    path('location', crud_location),
    path('location/<int:pk>', crud_location)
]
