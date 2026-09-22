"""Permissions explicites de la gestion des commandes."""
from rest_framework.permissions import BasePermission


class IsOrderParticipant(BasePermission):
    """Autorise uniquement l'acheteur, le vendeur ou un administrateur."""

    message = "Vous ne participez pas à cette commande."

    def has_object_permission(self, request, view, obj):
        return request.user.id in (obj.acheteur_id, obj.vendeur_id) or getattr(
            request.user, "role", None
        ) == "administrateur"
