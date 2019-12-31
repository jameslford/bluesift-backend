""" groups.urls """

from django.urls import path
from .views import (
    get_or_create_business,
    retailer_company_header,
    retailer_location_list_all,
    retailer_location_detail_header,
    services_list_all,
    service_detail_header
    )

urlpatterns = [
    path('create-business', get_or_create_business),
    # list urls
    path('retailers', retailer_location_list_all),
    path('retailers/detail', retailer_company_header),
    path('retailers/detail/<int:retailer_pk>', retailer_company_header),
    path('retailers/<str:prod_type>', retailer_location_list_all),
    path('retailer-locations/detail/<int:pk>', retailer_location_detail_header),
    # detail header urls
    path('pros/detail', service_detail_header),
    path('pros/detail/<int:pk>', service_detail_header),
    path('pros/<str:cat>', services_list_all),
]
