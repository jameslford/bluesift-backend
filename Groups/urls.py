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
    path('retailer-locations-list', retailer_location_list_all),
    path('retailer-locations-list/<str:prod_type>', retailer_location_list_all),
    path('services-list/<str:cat>', services_list_all),
    # detail header urls
    path('retailer/detail', retailer_company_header),
    path('retailer/detail/<int:retailer_pk>', retailer_company_header),
    path('retailer-locations/detail/<int:pk>', retailer_location_detail_header),
    path('services/detail', service_detail_header),
    path('services/detail/<int:pk>', service_detail_header)
]
