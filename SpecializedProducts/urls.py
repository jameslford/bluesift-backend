from django.urls import path
from .views import fs_products_list

urlpatterns = [
    path('finish-surfaces', fs_products_list),
]
