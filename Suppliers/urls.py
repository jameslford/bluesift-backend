
from django.urls import path
from .views import locations, crud_location, supplier_products

urlpatterns = [
    path('locations', locations),
    path('location', crud_location),
    path('location/<int:pk>', crud_location),
    path('products/<str:product_type>/<int:location_pk>', supplier_products),
    path('products', supplier_products)
]
