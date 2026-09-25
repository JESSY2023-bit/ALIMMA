"""Permissions explicites pour la modération."""
from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Autorise les modérateurs et les administrateurs."""

    message = "Cette action requiert le rôle modérateur."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated) and getattr(
            request.user, "role", None
        ) in {"moderateur", "administrateur"}
