from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from .views import (
    user_config,
    landing,
    generic_add,
    generic_delete,
    get_short_lib,
    pl_status_for_product,
    ut_features,
)


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("accounts/", include("Accounts.urls")),
    path("addresses/", include("Addresses.urls")),
    path("analytics/", include("Analytics.urls")),
    path("bs_admin/", include("BSadmin.urls")),
    path("groups/", include("Groups.urls")),
    path("products/", include("Products.urls")),
    path("profiles/", include("Profiles.urls")),
    path("projects/", include("Projects.urls")),
    path("search/", include("Search.urls")),
    path("suppliers/", include("Suppliers.urls")),
    path("add/", generic_add),
    path("add/<int:collection_pk>", generic_add),
    path("delete/<str:product_pk>", generic_delete),
    path("delete/<str:product_pk>/<int:collection_pk>", generic_delete),
    path("expanded-header", user_config),
    path("shortLib", get_short_lib),
    path("shortLib/<str:pk>", get_short_lib),
    path("pl_status/<str:pk>", pl_status_for_product),
    path("landing", landing),
    path("features/<str:user_type>", ut_features),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__", include(debug_toolbar.urls))] + urlpatterns
