from django.urls import path
from .views import products_list

urlpatterns = [
    path('filter/<str:product_type>', products_list),
    path('filter/<str:product_type>/<int:location_pk>', products_list),
]
