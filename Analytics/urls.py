""" Analytics.urls """
from django.urls import path
from .views import plan_views, retailer_view_analytics


urlpatterns = [
    path('plans', plan_views),
    path('retailer-views', retailer_view_analytics)
]
