''' profiles.urls.py '''
from django.urls import path
from .views import (
    supplier_library,
    supplier_list,
    supplier_detail,
    supplier_location,
    supplier_product
    )

urlpatterns = [
    path('supplier-library', supplier_library),
    path('supplier-list', supplier_list),
    path('cv-supplier-location/<int:pk>', supplier_detail),
    path('sv-supplier-location', supplier_location),
    path('sv-supplier-location/<int:pk>', supplier_location),
    path('supplier-product/<int:pk>', supplier_product)
]