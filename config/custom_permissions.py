from rest_framework.permissions import BasePermission


class RetailerPermission(BasePermission):
    """ permission for suppliers only """

    def has_permission(self, request, view):
        return request.user.is_supplier


class OwnerOrAdmin(BasePermission):
    """ permission for owner or admin - does not check for collection/owner association """

    def has_permission(self, request, view):
        if request.user.is_pro or request.user.is_supplier:
            profile = request.user.get_profile()
            return bool(profile.owner | profile.admin)
        return False

class OwnerDeleteAdminEdit(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not (user.is_pro or user.is_supplier):
            return False
        profile = user.get_profile()
        if request.method == 'DELETE':
            if profile.owner:
                return True
        if request.method == 'PUT':
            if profile.owner or profile.admin:
                return True
        return False

