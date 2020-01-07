from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from .views import (
    user_config,
    landing,
    task_progress,
    generic_business_list,
    generic_business_detail,
    generic_add,
    generic_delete,
    get_short_lib,
    pl_status_for_product
    )


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
    path('retailers/', include('Retailers.urls')),
    path('scraper/', include('Scraper.urls')),

    path('add/<int:collection_pk>', generic_add),
    path('delete/<int:product_pk>/<int:collection_pk>', generic_delete),
    path('expanded-header', user_config),
    path('shortLib', get_short_lib),
    path('shortLib/<str:pk>', get_short_lib),
    path('pl_status/<str:pk>', pl_status_for_product),

    path('business-detail/<str:category>/<int:pk>', generic_business_detail),
    path('businesses/<str:category>', generic_business_list),
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