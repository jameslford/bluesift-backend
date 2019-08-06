from django.urls import path
# from .views import retailer_location_products
from .views import (
    generic_add,
    generic_delete,
    get_project_products,
    retailer_products
    )


urlpatterns = [
    # path('retailer-products/<str:product_type>/<int:location_pk>', retailer_location_products)
    path('add', generic_add),
    path('add/<int:collection_pk>', generic_add),
    path('delete/<str:product_pk>', generic_delete),
    path('delete/<str:product_pk>/<int:collection_pk>', generic_delete),
    path('project-products/<int:project_pk>', get_project_products),
    path('retailer-products/<int:location_pk>/<str:product_type>', retailer_products)
]
