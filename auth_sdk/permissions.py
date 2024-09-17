from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

def user_has_perm(request, perm):
    return perm in getattr(request.user, 'permissions', [])

class HasPermission(BasePermission):
    def __init__(self, perm):
        self.perm = perm

    def has_permission(self, request, view):
        return user_has_perm(request, self.perm)