from django.urls import path
from .views import (
    alter_values,
    subgroup_list,
    subgroup_detail,
    stock_clean,
    update_field,
    view_products
    )

urlpatterns = [
    path('subgroups', subgroup_list),
    path('subgroup_detail/<int:pk>', subgroup_detail),
    path('default_products/<int:pk>', view_products),
    path('update_field', update_field),
    path('alter_values', alter_values),
    path('stock_clean', stock_clean)
]
