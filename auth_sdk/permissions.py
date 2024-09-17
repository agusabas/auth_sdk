from rest_framework.permissions import BasePermission
import requests
from django.conf import settings

class HasPermission(BasePermission):
    def __init__(self, required_permission):
        self.required_permission = required_permission

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Llamada al servicio de autenticación para verificar permisos
        response = requests.get(
            f"{settings.AUTH_SERVICE_URL}/api/user/permissions/{user.id}/",
            headers={"Authorization": f"Bearer {request.auth}"}
        )

        if response.status_code == 200:
            user_permissions = response.json().get('permissions', [])
            return self.required_permission in [perm['codename'] for perm in user_permissions]
        return False