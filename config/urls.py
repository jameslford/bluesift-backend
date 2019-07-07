from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include, reverse
from django.views.generic.base import RedirectView
# from .views import landing, get_short_lib, pl_status_for_product


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('Accounts.urls')),
    path('bbadmin/', include('BBadmin.urls')),
    path('specialized-products/', include('SpecializedProducts.urls')),
    path('mailing-list/', include('MailingList.urls')),
    path('orders/', include('Orders.urls')),
    path('products/', include('Products.urls')),
    path('scraper/', include('Scraper.urls')),
    # path('', landing),
    # path('get_short_lib/<int:pk>', get_short_lib),
    # path('get_short_lib/', get_short_lib),
    # path('grappelli/', include('grappelli.urls')),
    # path('carts/', include('Carts.urls')),
    # path('customerProfiles/', include('CustomerProfiles.urls'), name='customer_profiles'),
    # path('pl_status/<str:pk>', pl_status_for_product),
    # path('supplierProfiles/', include('Profiles.urls'), name='profiles'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__', include(debug_toolbar.urls))
    ] + urlpatterns
