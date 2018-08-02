
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include, re_path
from rest_framework.authtoken import views
from django.conf.urls import url
from .views import landing



urlpatterns = [
    path('', landing, name = 'home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('Accounts.urls')),
    path('products/', include('Products.urls')),
    path('profiles/', include('Profiles.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
