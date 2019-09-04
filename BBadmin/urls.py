from django.urls import path
from .views import dashboard


urlpatterns = [
    path('dashboard/', dashboard),
    # path('check/', admin_check),
    # path('user/<int:pk>', user_details)
]