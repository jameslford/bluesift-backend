# ''' profiles.urls.py '''
from django.urls import path
from .views import get_short_lib, pl_status_for_product
# from .views import (
#     company_account,
#     supplier_list,
#     cv_supplier_location,
#     cv_supplier_location_content,
#     sv_supplier_location,
#     supplier_product
#     )

urlpatterns = [
    path('shortLib', get_short_lib),
    path('shortLib/<str:pk>', get_short_lib),
    path('pl_status/<str:pk>', pl_status_for_product)
]

# urlpatterns = [
#     path('company-account', company_account),
#     path('sv-supplier-location', sv_supplier_location),
#     path('sv-supplier-location/<int:pk>', sv_supplier_location),
#     path('supplier-product/<int:proj_pk>', supplier_product),
#     path('supplier-product/<int:proj_pk>/<str:prod_pk>', supplier_product),
#     path('supplier-list', supplier_list),
#     path('cv-supplier-location/<int:pk>', cv_supplier_location),
#     path('cv-supplier-location-content/<int:pk>', cv_supplier_location_content)
# ]
