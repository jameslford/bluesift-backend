
from django.urls import path
from .views import locations, crud_location, retailer_products

urlpatterns = [
    path('locations', locations),
    path('location', crud_location),
    path('location/<int:pk>', crud_location),
    path('products/<str:product_type>/<int:location_pk>', retailer_products),
    path('products', retailer_products)
]
