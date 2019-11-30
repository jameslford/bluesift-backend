""" Analytics.urls """
from django.urls import path
from .views import all_retailer_location_views, group_views, test, plan_views


urlpatterns = [
    path('retailer-views', all_retailer_location_views),
    path('retailer-views/<int:user_pk>', all_retailer_location_views),
    path('groups', group_views),
    path('plans', plan_views),
    path('test/<int:group_pk>', test),
    path('test/<int:group_pk>/<str:interval>', test)
]
