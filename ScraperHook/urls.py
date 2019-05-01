from django.urls import path
from .views import scraper_dashboard

urlpatterns = [
    path('dashboard', scraper_dashboard),
]
