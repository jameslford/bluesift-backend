""" Analytics.urls """
from django.urls import path
from .views import supplier_view_records

urlpatterns = [path("supplier-views", supplier_view_records)]
