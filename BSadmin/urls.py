from django.urls import path
from .views import scrape, refresh_tree

urlpatterns = [
    path('scrapers', scrape),
    path('trees', refresh_tree)
]