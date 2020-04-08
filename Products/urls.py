from django.urls import path, re_path
from .views import product_detail, products_list, product_detail_quick

urlpatterns = [
    path('detail/<str:pk>', product_detail),
    path('quick/<str:pk>', product_detail_quick),
    path('filter', products_list),
    re_path(r'^filter/([\w /]*)/$', products_list),
]
