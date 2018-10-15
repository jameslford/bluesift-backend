''' profiles.urls.py '''
from django.urls import path
from .views import get_lib, get_short_lib, append_lib, supplier_list

urlpatterns = [
    path('getLib', get_lib),
    path('getShortLib', get_short_lib),
    path('appendLib', append_lib),
    path('supplierList', supplier_list)
]
