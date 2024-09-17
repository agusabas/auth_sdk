from rest_framework.permissions import BasePermission
from .models import AnonymousUser

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

def user_has_perm(request, perm):
    if isinstance(request.user, AnonymousUser):
        return False
    return perm in getattr(request.user, 'permissions', [])

class HasPermission(BasePermission):
    def __init__(self, *perms):
        self.perms = perms

    def has_permission(self, request, view):
        return any(user_has_perm(request, perm) for perm in self.perms)