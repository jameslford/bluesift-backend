''' profiles.urls.py '''
from django.urls import path
from .views import (
    company_account,
    supplier_list,
    cv_supplier_location,
    sv_supplier_location,
    supplier_product
    )

urlpatterns = [
    path('company-account', company_account),
    path('sv-supplier-location', sv_supplier_location),
    path('sv-supplier-location/<int:pk>/', sv_supplier_location),
    path('supplier-product', supplier_product),
    path('supplier-product/<int:pk>', supplier_product),
    path('supplier-list', supplier_list),
    path('cv-supplier-location/<int:pk>', cv_supplier_location)
]
