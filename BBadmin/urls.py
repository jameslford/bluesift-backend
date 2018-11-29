from django.urls import path
from .views import dashboard, admin_check, user_details


urlpatterns = [
    path('dashboard/', dashboard),
    path('check/', admin_check),
    path('user/<int:pk>', user_details)
]