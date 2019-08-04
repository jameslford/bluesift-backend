from rest_framework.permissions import BasePermission


class RetailerPermission(BasePermission):
    """ permission for suppliers only """

    def has_permission(self, request, view):
        return request.user.is_supplier


class OwnerOrAdmin(BasePermission):
    """ permission for owner or admin - does not check for collection/owner association """

    def has_permission(self, request, view):
        if request.user.is_pro or request.user.is_admin:
            return bool(request.user.is_owner | request.user.is_admin)
        return True
