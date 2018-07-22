from django.urls import path, include, re_path
from .views import product_list, ProductDetail

urlpatterns = [
    path('all', product_list),
    path('detail/<int:pk>', ProductDetail.as_view())
]