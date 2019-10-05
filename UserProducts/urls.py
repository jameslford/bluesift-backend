""" UserProduct.urls """
from django.urls import path
from .views import (
    generic_add,
    generic_delete,
    edit_retailer_product,
    retailer_products
    )


urlpatterns = [
    path('add', generic_add),
    path('add/<int:collection_pk>', generic_add),
    path('delete/<str:product_pk>', generic_delete),
    path('delete/<str:product_pk>/<int:collection_pk>', generic_delete),
    path('edit-retailer-products', edit_retailer_product),
    path('retailer-products<int:location_pk>', retailer_products),
]
