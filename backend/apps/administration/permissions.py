"""Permission explicite de l'administration."""
from rest_framework.permissions import BasePermission


class IsAdministrator(BasePermission):
    """Autorise strictement le rôle administrateur ALIMMA."""

    message = "Cette action requiert le rôle administrateur."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated) and getattr(
            request.user, "role", None) == "administrateur"
