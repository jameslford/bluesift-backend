from django.urls import path
from .views import( checkout_permission )

urlpatterns = [
    path('ck_perm/', checkout_permission),
    path('ck_perm/<int:pk>', checkout_permission)
]