from django.urls import path
from .views import (
    alter_values,
    subgroup_list,
    subgroup_detail,
    stock_clean,
    update_field,
    view_products,
    department_detail,
    get_departments
    )

urlpatterns = [
    path('subgroups', subgroup_list),
    path('subgroup_detail/<int:pk>', subgroup_detail),
    path('scraper_product/<int:pk>', view_products),
    path('department_list', get_departments),
    path('department_detail/<int:pk>', department_detail),
    path('update_field', update_field),
    path('alter_values', alter_values),
    path('stock_clean', stock_clean)
]
