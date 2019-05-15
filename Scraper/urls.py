from django.urls import path
from .views import (
    subgroup_list,
    subgroup_detail
    )

urlpatterns = [
    path('subgroups', subgroup_list),
    path('subgroup_detail/<int:pk>', subgroup_detail)
]
