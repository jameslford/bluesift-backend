""" groups.urls """

from django.urls import path
from .views import (
    retailer_company_header,
    retailer_location_list_all,
    retailer_location_detail_header,
    services_list_all,
    service_detail_header
    )

urlpatterns = [
    path('retailer/detail', retailer_company_header),
    path('retailer/detail/<int:retailer_pk>', retailer_company_header),
    path('retailer-locations/<str:prod_type>', retailer_location_list_all),
    path('retailer-locations/detail/<int:pk>', retailer_location_detail_header),
    path('services/<str:cat>', services_list_all),
    path('services/detail/<int:pk>', service_detail_header)
]
