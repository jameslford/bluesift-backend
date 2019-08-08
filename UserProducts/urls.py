""" UserProduct.urls """
from django.urls import path
from .views import (
    generic_add,
    generic_delete,
    get_project_products,
    retailer_products,
    edit_retailer_product
    )


urlpatterns = [
    path('add', generic_add),
    path('add/<int:collection_pk>', generic_add),
    path('delete/<str:product_pk>', generic_delete),
    path('delete/<str:product_pk>/<int:collection_pk>', generic_delete),
    path('project-products/<int:project_pk>', get_project_products),
    path('retailer-products/<int:location_pk>/<str:product_type>', retailer_products),
    path('edit-retailer-products', edit_retailer_product),
]
