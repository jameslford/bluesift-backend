from rest_framework.permissions import BasePermission


class RetailerPermission(BasePermission):
    """ permission for suppliers only """

    def has_permission(self, request, view):
        return request.user.is_supplier
