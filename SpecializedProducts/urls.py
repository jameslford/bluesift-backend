from django.urls import path
from .views import fs_products_list

urlpatterns = [
    path('all', fs_products_list),
]
