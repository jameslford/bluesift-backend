""" groups.urls """

from django.urls import path
from .views import (
    company_crud,
    public_company_view
    )

urlpatterns = [
    path('', company_crud),
    path('<int:pk>', public_company_view)
    ]

    # get_or_create_business,
    # company_detail,
    # path('create-business', get_or_create_business),
    # path('detail', company_detail),
