''' profiles.urls.py '''
from django.urls import path
from .views import get_short_lib, pl_status_for_product, profile_crud


urlpatterns = [
    path('profile', profile_crud),
    path('shortLib', get_short_lib),
    path('shortLib/<str:pk>', get_short_lib),
    path('pl_status/<str:pk>', pl_status_for_product)
]
