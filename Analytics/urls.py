""" Analytics.urls """
from django.urls import path
from .views import plan_views


urlpatterns = [
    path('plans', plan_views)
]
