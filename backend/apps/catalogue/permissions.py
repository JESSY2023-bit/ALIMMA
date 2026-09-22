"""Permissions explicites du catalogue."""
from rest_framework.permissions import BasePermission


class IsAnnonceOwner(BasePermission):
    """Réserve la modification d'une annonce à son vendeur."""

    message = "Seul le vendeur de l'annonce peut effectuer cette action."

    def has_object_permission(self, request, view, obj):
        return obj.vendeur_id == request.user.id
