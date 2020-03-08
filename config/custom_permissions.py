from rest_framework import permissions
from django.conf import settings


class IsAdminorReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_admin:
                return True
            return False

class RetailerPermission(permissions.BasePermission):
    """ permission for suppliers only """

    def has_permission(self, request, view):
        return request.user.is_supplier


class OwnerOrAdmin(permissions.BasePermission):
    """ permission for owner or admin - does not check for collection/owner association """

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.user.is_supplier:
            profile = request.user.get_profile()
            return bool(profile.owner | profile.admin)
        return True


class OwnerDeleteAdminEdit(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_supplier:
            return False
        profile = user.get_profile()
        if request.method == 'DELETE':
            if not profile.owner:
                return False
        if request.method == 'PUT':
            if not (profile.owner or profile.admin):
                return False
        return True

class PrivateSupplierCrud(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_supplier:
            return False
        profile = user.get_profile()

        if request.method == 'POST' and profile:
            if profile.owner:
                return True

        if request.method == 'DELETE':
            if profile.owner:
                return True

        if request.method == 'PUT':
            if profile.owner or profile.admin:
                return True

        if request.method == 'GET':
            return True

        return False


    # def has_object_permission(self, request, view, obj):
    #     pass


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
            and request.user.admin
        )

class AllowAllExceptStaging(permissions.BasePermission):

    def has_permission(self, request, view):
        if settings.ENVIRONMENT == 'staging':
            return bool(
                request.user and
                request.user.admin
            )
        return True

class SupplierAdminPro(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        user = request.user
        if user.admin:
            return True
        if user.is_supplier:
            return True
        return False
