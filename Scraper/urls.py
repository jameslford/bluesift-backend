from django.urls import path
from .views import (
    subgroup_detail,
    stock_clean,
    view_products,
    department_list,
    department_detail,
    subgroups_list,
    update_field
    )

urlpatterns = [
    path('departments', department_list),
    path('department_detail/<str:dep>', department_detail),
    path('subgroups_list', subgroups_list),
    path('subgroups_list/<str:department>', subgroups_list),
    path('subgroup_detail/<int:pk>', subgroup_detail),
    path('supgroup_clean', stock_clean),
    path('subgroup_scrape', stock_clean),
    path('update_field/<int:pk>', update_field),
    path('view_products/<int:pk>', view_products)
]
