"""Permissions explicites pour la modération."""
from rest_framework.permissions import BasePermission


class EstModerateurOuAdmin(BasePermission):
    """Autorise les modérateurs et les administrateurs."""

    message = "Cette action requiert le rôle modérateur."

    def has_permission(self, request, view):
        """Accepte un JWT authentifié portant un rôle de modération autorisé."""
        return bool(request.user and request.user.is_authenticated) and getattr(
            request.user, "role", None
        ) in {"moderateur", "administrateur"}


# Le nom historique est conservé afin de ne pas rompre les imports existants.
IsModerator = EstModerateurOuAdmin
