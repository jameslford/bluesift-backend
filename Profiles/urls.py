''' profiles.urls.py '''
from django.urls import path
from .views import (
    supplier_library,
    supplier_list,
    cv_supplier_location,
    sv_supplier_location,
    supplier_product
    )

urlpatterns = [
    path('supplier-library', supplier_library),
    path('sv-supplier-location', sv_supplier_location),
    path('sv-supplier-location/<int:pk>', sv_supplier_location),
    path('supplier-product/<int:pk>', supplier_product),
    path('supplier-list', supplier_list),
    path('cv-supplier-location/<int:pk>', cv_supplier_location)
]
