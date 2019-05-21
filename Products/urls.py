from django.urls import path, include, re_path
from .views import product_detail

urlpatterns = [
    path('detail/<str:pk>', product_detail)
]
