"""Permissions explicites du catalogue."""
from rest_framework.permissions import BasePermission


class EstProprietaireAnnonce(BasePermission):
    """Réserve la modification d'une annonce à son vendeur."""

    message = "Seul le vendeur de l'annonce peut effectuer cette action."

    def has_object_permission(self, request, view, obj):
        """Vérifie que le compte JWT est bien le vendeur de l'annonce ciblée."""
        return obj.vendeur_id == request.user.id


class PeutConsulterAnnonce(BasePermission):
    """Autorise le détail public ou l'accès restreint aux annonces non actives."""

    message = "Cette annonce n'est pas accessible avec ce compte."

    def has_object_permission(self, request, view, obj):
        """Contrôle les comptes authentifiés autorisés sur une annonce non active.

        Une requête anonyme est laissée à la vue afin qu'elle puisse répondre
        volontairement par 404, sans que DRF ne la transforme d'abord en 401.
        """
        if obj.statut == obj.Statut.ACTIVE:
            return True
        if not request.user.is_authenticated:
            return True
        return obj.vendeur_id == request.user.id or getattr(request.user, "role", None) in {
            "moderateur",
            "administrateur",
        }


# Alias conservé pour les éventuels consommateurs internes utilisant le nom
# anglais antérieur. Les nouvelles vues utilisent le nom métier français.
IsAnnonceOwner = EstProprietaireAnnonce
