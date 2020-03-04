from django.urls import path
from .views import scrape, refresh_tree

urlpatterns = [
    path('scrape', scrape),
    path('scrape/<int:pk>', scrape),
    path('refresh_tree', refresh_tree)
]