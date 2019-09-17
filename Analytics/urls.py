""" Analytics.urls """
from django.urls import path
from .views import plan_views, all_retailer_location_views


urlpatterns = [
    path('plans', plan_views),
    path('retailer-views', all_retailer_location_views),
    path('retailer-views/<int:user_pk>', all_retailer_location_views)
]
