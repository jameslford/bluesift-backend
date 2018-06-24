# API.urls.py

from django.urls import path
from .views import ProductList, supplier_signup


urlpatterns = [
path('products/', ProductList.as_view()),
path('register/', supplier_signup)
]
