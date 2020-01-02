from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from .views import user_config, landing, task_progress


urlpatterns = [
    # path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('addresses/', include('Addresses.urls')),
    path('accounts/', include('Accounts.urls')),
    path('analytics/', include('Analytics.urls')),
    # path('bbadmin/', include('BBadmin.urls')),
    path('groups/', include('Groups.urls')),
    path('collections/', include('UserProductCollections.urls')),
    path('expanded-header', user_config),
    path('landing', landing),
    path('mailing-list/', include('MailingList.urls')),
    # path('orders/', include('Orders.urls')),
    path('profiles/', include('Profiles.urls')),
    path('products/', include('Products.urls')),
    path('scraper/', include('Scraper.urls')),
    path('schedule/', include('Schedule.urls')),
    path('task-progress', task_progress),
    path('user-products/', include('UserProducts.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__', include(debug_toolbar.urls))
    ] + urlpatterns
