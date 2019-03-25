from django.urls import path, include, re_path
from .views import product_list, get_product

urlpatterns = [
    path('all/<str:cat>', product_list),
    path('detail/<int:pk>', get_product)
]