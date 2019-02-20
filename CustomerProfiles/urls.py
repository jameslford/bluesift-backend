from django.urls import path
from .views import (
    customer_library,
    customer_project,
    customer_product,
    customer_project_application
)


urlpatterns = [
    path('customer-library', customer_library),
    path('customer-project', customer_project),
    path('customer-project/<int:pk>', customer_project),
    path('customer-product', customer_product),
    path('customer-project-application', customer_project_application),
    path('customer-project-application/<int:pk>', customer_project_application)
]