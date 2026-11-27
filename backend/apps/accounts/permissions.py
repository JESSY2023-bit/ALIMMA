"""Permissions explicites propres aux comptes."""
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class TelephoneNonVerifie(PermissionDenied):
    """Refus explicite des opérations nécessitant un numéro confirmé."""

    default_code = "PHONE_NOT_VERIFIED"
    default_detail = "Veuillez vérifier votre numéro de téléphone."


class TelephoneVerifie(BasePermission):
    """Exige une vérification OTP avant les actions commerciales sensibles."""

    def has_permission(self, request, view):
        """Renvoie le code d'erreur métier attendu au lieu d'un 403 générique."""
        if getattr(request.user, "telephone_verifie", False):
            return True
        raise TelephoneNonVerifie()


class EstAdministrateur(BasePermission):
    """Réserve explicitement une action au rôle administrateur ALIMMA."""

    message = "Cette action requiert le rôle administrateur."

    def has_permission(self, request, view):
        """Autorise uniquement un utilisateur JWT actif de rôle administrateur."""
        return bool(request.user and request.user.is_authenticated) and getattr(
            request.user, "role", None
        ) == "administrateur"


class IsSelfOrAdministrator(BasePermission):
    """Autorise un utilisateur lui-même ou un administrateur."""

    message = "Cette action est réservée au propriétaire du compte."

    def has_object_permission(self, request, view, obj):
        """Compare l'objet demandé au compte JWT, sauf pour un administrateur."""
        return obj == request.user or getattr(request.user, "role", None) == "administrateur"
