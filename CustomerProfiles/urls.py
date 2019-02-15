from django.urls import path
from .views import (
    customer_library,
    customer_project
)


urlpatterns = [
    path('customer-library', customer_library),
    path('customer-project', customer_project)
]