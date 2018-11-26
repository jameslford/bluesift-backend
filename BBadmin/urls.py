from django.urls import path
from .views import dashboard, admin_check


urlpatterns = [
    path('dashboard/', dashboard),
    path('check/', admin_check)
]