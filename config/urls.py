from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include, reverse
from django.views.generic.base import RedirectView
from .views import landing, get_short_lib


urlpatterns = [
    path('', landing),
    path('admin/', admin.site.urls),
    # path('grappelli/', include('grappelli.urls')),
    path('get_short_lib/', get_short_lib),
    path('accounts/', include('Accounts.urls')),
    path('bbadmin/', include('BBadmin.urls')),
    path('carts/', include('Carts.urls')),
    path('customerProfiles/', include('CustomerProfiles.urls'), name='customer_profiles'),
    path('finish-surfaces/', include('FinishSurfaces.urls')),
    path('mailing-list/', include('MailingList.urls')),
    path('orders/', include('Orders.urls')),
    path('products/', include('Products.urls')),
    path('scraper/', include('Scraper.urls')),
    path('supplierProfiles/', include('Profiles.urls'), name='profiles'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__', include(debug_toolbar.urls))
    ] + urlpatterns
