from django.urls import path
from .views import add_to_cart, cart_details


urlpatterns = [
    path('addtocart/', add_to_cart),
    path('details/', cart_details),
]
