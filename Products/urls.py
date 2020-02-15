from django.urls import path, include, re_path
from .views import product_detail, products_list, product_detail_quick

urlpatterns = [
    path('detail/<str:pk>', product_detail),
    path('quick/<str:pk>', product_detail_quick),
    path('filter', products_list),
    path('filter/<str:product_type>', products_list),
    path('filter/<str:product_type>/<str:sub_product>', products_list),
]
