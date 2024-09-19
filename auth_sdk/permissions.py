from rest_framework.permissions import BasePermission
from .models import AnonymousUser

class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not isinstance(request.user, AnonymousUser) and request.user.is_authenticated

def user_has_perm(request, perm):
    if isinstance(request.user, AnonymousUser):
        return False
    return perm in getattr(request.user, 'user_permissions', [])

class HasPermission(BasePermission):
    def __init__(self, *perms):
        self.perms = perms

    def __call__(self):
        return self

    def has_permission(self, request, view):
        return any(user_has_perm(request, perm) for perm in self.perms)
    
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()