from django.urls import path
from .views import (
    customer_library,
    customer_project,
    customer_product
)


urlpatterns = [
    path('customer-library', customer_library),
    path('customer-project', customer_project),
    path('customer-product', customer_product)
]