from django.urls import path
from .views import (
    dashboard,
    demo,
    scrape,
    refresh_tree,
    get_final_images,
    convert_geometries,
    refresh_facets,
    refresh_search,
    clean_scraper_group,
)

urlpatterns = [
    path("dashboard", dashboard),
    path("demo", demo),
    path("scrapers", scrape),
    path("scrapers/<int:pk>", scrape),
    path("trees", refresh_tree),
    path("images/<int:pk>", get_final_images),
    path("geometry/<int:pk>", convert_geometries),
    path("facets", refresh_facets),
    path("search", refresh_search),
    path("clean/<int:pk>", clean_scraper_group),
]
