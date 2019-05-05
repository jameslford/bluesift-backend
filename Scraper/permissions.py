from rest_framework import permissions
from django.conf import settings


class ScraperHookPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        if settings.ENVIRONMENT == 'production':
            return False
        if settings.ENVIRONMENT == 'staging':
            return bool(request.user and request.user.is_admin)
        if settings.ENVIRONMENT == 'local':
            return True
        return False
