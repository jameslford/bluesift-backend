from django.urls import path, include, re_path
from .views import product_detail, products_list

urlpatterns = [
    path('detail/<str:pk>', product_detail),
    path('filter/<str:product_type>', products_list),
    path('filter/<str:product_type>/<int:location_pk>', products_list),
]
