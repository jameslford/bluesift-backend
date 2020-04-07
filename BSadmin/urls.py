from django.urls import path
from .views import scrape

urlpatterns = [
    path('scrapers', scrape),
]