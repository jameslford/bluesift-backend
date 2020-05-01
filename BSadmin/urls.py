from django.urls import path
from .views import (
    scrape,
    refresh_tree,
    get_final_images,
    convert_geometries,
    refresh_facets,
    refresh_search,
    refresh_demo_supplier_products,
)

urlpatterns = [
    path("scrapers", scrape),
    path("scrapers/<int:pk>", scrape),
    path("trees", refresh_tree),
    path("images/<int:pk>", get_final_images),
    path("geometry/<int:pk>", convert_geometries),
    path("facets", refresh_facets),
    path("search", refresh_search),
    path("refresh_demo_supplier_products", refresh_demo_supplier_products),
]
