""" groups.urls """

from django.urls import path
from .views import (
    get_or_create_business,
    company_detail,
    )

urlpatterns = [
    path('create-business', get_or_create_business),
    path('detail', company_detail),
    ]
