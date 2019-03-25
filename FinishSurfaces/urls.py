from django.urls import path
from .views import fs_products_list, fs_product_detail

urlpatterns = [
    path('all', fs_products_list),
    path('detail/<int:pk>', fs_product_detail)
]
