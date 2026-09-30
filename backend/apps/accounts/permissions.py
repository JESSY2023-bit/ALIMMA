"""Permissions explicites propres aux comptes."""
from rest_framework.permissions import BasePermission


class IsSelfOrAdministrator(BasePermission):
    """Autorise un utilisateur lui-même ou un administrateur."""

    message = "Cette action est réservée au propriétaire du compte."

    def has_object_permission(self, request, view, obj):
        """Compare l'objet demandé au compte JWT, sauf pour un administrateur."""
        return obj == request.user or getattr(request.user, "role", None) == "administrateur"
