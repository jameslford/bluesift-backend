""" groups.urls """

from django.urls import path
from .views import (
    get_or_create_business,
    pro_company_detail,
    pro_company_detail_public,
    retailer_company_detail,
    retailer_company_detail_public
    )

urlpatterns = [
    path('create-business', get_or_create_business),
    path('retailer', retailer_company_detail),
    path('retailer/<int:retailer_pk>', retailer_company_detail_public),
    path('pro', pro_company_detail),
    path('pro/<int:pk>', pro_company_detail_public)
    ]
