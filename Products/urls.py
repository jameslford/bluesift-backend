from django.urls import path, include, re_path
from .views import get_product

urlpatterns = [
    # path('all', product_list),
    path('detail/<int:pk>', get_product)
]