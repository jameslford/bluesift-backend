from django.urls import path, include, re_path
from .views import (
    retailer_list_all,
    services_list_all,
    retailer_detail_header,
    service_detail_header
    )

urlpatterns = [
    path('retailers', retailer_list_all),
    path('services/<str:cat>', services_list_all),
    path('retailers/detail/<int:pk>', retailer_detail_header),
    path('services/detail/<int:pk>', service_detail_header)
]
