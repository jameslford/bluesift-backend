from django.urls import path
from .views import (
    subgroup_list,
    subgroup_detail,
    view_products,
    update_revised
    )

urlpatterns = [
    path('subgroups', subgroup_list),
    path('subgroup_detail/<int:pk>', subgroup_detail),
    path('default_products/<int:pk>', view_products),
    path('update_field', update_revised)
]
