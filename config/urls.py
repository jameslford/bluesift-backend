from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from .views import user_config, landing, task_progress, generic_business_list, generic_add, generic_delete


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('Accounts.urls')),
    path('addresses/', include('Addresses.urls')),
    path('analytics/', include('Analytics.urls')),
    path('groups/', include('Groups.urls')),
    path('mailing-list/', include('MailingList.urls')),
    path('products/', include('Products.urls')),
    path('profiles/', include('Profiles.urls')),
    path('projects/', include('Projects.urls')),
    path('scraper/', include('Scraper.urls')),

    path('add', generic_add),
    path('delete/<int:product_pk>', generic_delete),
    path('delete/<int:product_pk>/<int:collection_pk>', generic_delete),
    path('expanded-header', user_config),
    path('businesses/<str:category>', generic_business_list),
    path('businesses/<str:category>/<str:service>', generic_business_list),
    path('landing', landing),
    path('task-progress', task_progress),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__', include(debug_toolbar.urls))
    ] + urlpatterns

    # path('admin/doc/', include('django.contrib.admindocs.urls')),
    # path('bbadmin/', include('BBadmin.urls')),
    # path('collections/', include('UserProductCollections.urls')),
    # path('orders/', include('Orders.urls')),
    # path('schedule/', include('Schedule.urls')),
    # path('user-products/', include('UserProducts.urls'))