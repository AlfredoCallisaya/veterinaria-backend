# usuarios/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.roles.filter(nombre="Administrador").exists()


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.roles.filter(nombre="Administrador").exists()
