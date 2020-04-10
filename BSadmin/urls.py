from django.urls import path
from .views import scrape, refresh_tree, get_final_images

urlpatterns = [
    path('scrapers', scrape),
    path('scrapers/<int:pk>', scrape),
    path('trees', refresh_tree),
    path('images/<int:pk>', get_final_images)
]