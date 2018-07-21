from django.urls import path, include, re_path
from .views import product_list

urlpatterns = [
    path('all', product_list)
]