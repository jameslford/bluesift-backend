from django.urls import path, include, re_path
from .views import fs_product_list

urlpatterns = [
    path('all', fs_product_list),
    # path('detail/<int:pk>', get_product)
]