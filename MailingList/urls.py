from django.urls import path, include, re_path
from .views import add_to_mailinglist

urlpatterns = [
    path('add-to-mailing-list', add_to_mailinglist)
]