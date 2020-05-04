from django.urls import path
from .views import (
    crud_location,
    crud_supplier_products,
    public_locations_list_view,
    public_location_detail_view,
    private_locations_list,
)

urlpatterns = [
    path("public-locations", public_locations_list_view),
    path("public-locations/<str:category>", public_locations_list_view),
    path("public-location/<int:pk>", public_location_detail_view),
    path("locations", private_locations_list),
    path("location", crud_location),
    path("location/<int:pk>", crud_location),
    path("products/<str:product_type>", crud_supplier_products),
    path("products", crud_supplier_products),
]
