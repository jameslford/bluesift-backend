
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from .views import landing, get_short_lib, append_lib


urlpatterns = [
    path('', landing, name='home'),
    path('admin/', admin.site.urls),
    path('get_short_lib/', get_short_lib),
    # path('append_lib', append_lib),
    path('accounts/', include('Accounts.urls')),
    path('carts/', include('Carts.urls')),
    path('products/', include('Products.urls')),
    path('customerProfiles/', include('CustomerProfiles.urls')),
    path('supplierProfiles/', include('Profiles.urls'), name='profiles'),
    path('orders/', include('Orders.urls')),
    path('bbadmin/', include('BBadmin.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__', include(debug_toolbar.urls))
    ] + urlpatterns