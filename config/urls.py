
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from .views import landing



urlpatterns = [
    path('', landing, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('Accounts.urls')),
    path('carts/', include('Carts.urls')),
    path('products/', include('Products.urls')),
    path('profiles/', include('Profiles.urls')),
    path('orders/', include('Orders.urls')),
    path('bbadmin/', include('BBadmin.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
