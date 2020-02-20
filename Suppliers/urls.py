
from django.urls import path
from .views import crud_location, crud_supplier_products, public_locations_list_view, public_location_detail_view

urlpatterns = [
    path('locations', public_locations_list_view),
    path('locations/<str:category>', public_locations_list_view),
    path('public-location/<int:pk>', public_location_detail_view),
    path('location', crud_location),
    path('location/<int:pk>', crud_location),
    path('products/<str:product_type>/<int:location_pk>', crud_supplier_products),
    path('products', crud_supplier_products)
]
