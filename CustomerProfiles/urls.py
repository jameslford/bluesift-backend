from django.urls import path
from .views import (
    customer_library
)


urlpatterns = [
    path('customer-library', customer_library)
]