from django.urls import path
from .views import retailer_location_products

urlpatterns = [
    path('retailer-products/<str:product_type>/<int:location_pk>', retailer_location_products)
]
