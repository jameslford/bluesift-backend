from django.urls import path
from .views import (
    alter_values,
    subgroup_list,
    subgroup_detail,
    stock_clean,
    update_field,
    view_products,
    department_detail,
    get_departments,
    run_subgroup_command,
    update_subgroup_property
    )

urlpatterns = [
    path('subgroups', subgroup_list),
    path('subgroup_detail/<int:pk>', subgroup_detail),
    path('scraper_product/<int:pk>', view_products),
    path('department_list', get_departments),
    path('department_detail/<int:pk>', department_detail),
    path('subgroup_command', run_subgroup_command),
    path('alter_sb_prop/<int:pk>', update_subgroup_property),
    path('update_field', update_field),
    path('alter_values', alter_values),
    path('stock_clean', stock_clean)
]
