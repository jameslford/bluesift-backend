''' profiles.urls.py '''
from django.urls import path
from .views import(
    get_lib,
    get_short_lib,
    append_lib,
    supplier_list,
    supplier_detail,
    supplier_location,
    supplier_product
    )

urlpatterns = [
    path('getLib', get_lib),
    path('getShortLib', get_short_lib),
    path('appendLib', append_lib),
    path('supplierList', supplier_list),
    path('supplierDetails/<int:pk>', supplier_detail),
    path('supplierLocation', supplier_location),
    path('supplierLocation/<int:pk>', supplier_location),
    path('supplierProduct/<int:pk>/', supplier_product)
]
