from django.urls import path
from .views import (
    alter_values,
    subgroup_detail,
    stock_clean,
    view_products,
    department_values,
    department_subgroups,
    get_departments,
    run_subgroup_command,
    update_subgroup_property,
    # update_subgroup_field,
    # update_department_field
    update_field
    )

urlpatterns = [
    path('departments', get_departments),
    path('department_values/<str:dep>', department_values),
    path('department_subgroups', department_subgroups),
    path('department_subgroups/<str:department>', department_subgroups),
    path('subgroup_command', run_subgroup_command),
    path('subgroup_detail/<int:pk>', subgroup_detail),
    path('view_products/<int:pk>', view_products),
    path('alter_sb_prop/<int:pk>', update_subgroup_property),
    path('update_field/<int:pk>', update_field),
    # path('view_products/<int:pk>/<str:search_group>', view_products),
    # path('update_subgroup_field/<int:subgroup_pk>', update_subgroup_field),
    # path('update_department_field/<int:department_pk>', update_department_field),
    path('alter_values', alter_values),
    path('stock_clean', stock_clean)
]
