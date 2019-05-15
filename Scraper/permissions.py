from rest_framework import permissions
from django.conf import settings


class StagingAdminOnly(permissions.BasePermission):
    """only allows view if user is admin and on staging server
    """
    def has_permission(self, request, view):
        return bool(
            settings.ENVIRONMENT == 'staging'
            and request.user
            and request.user.is_admin
            )


class StagingorLocalAdmin(permissions.BasePermission):
    """only allows view if user is admin and on staging or local server
    """
    def has_permission(self, request, view):
        return bool(
            bool(settings.ENVIRONMENT == 'staging' or settings.ENVIRONMENT == 'local')
            and request.user
            and request.user.is_admin
        )
