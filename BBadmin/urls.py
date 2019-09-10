from django.urls import path
from .views import dashboard


urlpatterns = [
    path('dashboard/', dashboard),
    # path('plans', get_plans),
    # path('check/', admin_check),
    # path('user/<int:pk>', user_details)
]