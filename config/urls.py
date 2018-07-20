"""BBdjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include, re_path
from rest_framework.authtoken import views
from django.conf.urls import url
from .views import landing
from API.views import (
                        create_user,
                        create_supplier, 
                        activate, 
                        login, 
                        get_token, 
                        product_list,
                        user_library
                        )

urlpatterns = [
    path('', landing, name = 'home'),
    path('admin/', admin.site.urls),
    path('products/', product_list),
    path('registerUser/', create_user),
    path('registerSupplier/', create_supplier),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('login/', login),
    path('get_token/', get_token),
    path('library/', user_library ),

   
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
