from django.urls import path
from .views import add_to_cart


urlpatterns = [
    path('addtocart/', add_to_cart)
]
