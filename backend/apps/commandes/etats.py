"""Machine d'états transactionnelle des commandes d'achat direct."""
from django.db import transaction
from rest_framework.exceptions import APIException

from apps.catalogue.models import Annonce

from .models import Commande, HistoriqueStatutCommande


class TransitionInvalide(APIException):
    """Signale une transition absente du cycle métier sans exposer de détail interne."""

    status_code = 409
    default_code = "INVALID_TRANSITION"
    default_detail = "Cette transition de commande n'est pas autorisée."


# Les rôles décrivent le participant à la commande, pas seulement son enum
# utilisateur. ``systeme`` est exclusivement réservé aux tâches internes.
TRANSITIONS_AUTORISEES = {
    Commande.Statut.ATTENTE_PAIEMENT: {
        Commande.Statut.ATTENTE_VENDEUR: {"systeme"},
        Commande.Statut.ANNULEE: {"systeme"},
    },
    Commande.Statut.ATTENTE_VENDEUR: {
        Commande.Statut.ACCEPTEE: {"vendeur"},
        Commande.Statut.ANNULEE: {"vendeur", "acheteur", "systeme"},
    },
    Commande.Statut.ACCEPTEE: {
        Commande.Statut.EXPEDIEE: {"vendeur"},
        Commande.Statut.LIVREE: {"vendeur", "livreur"},
        Commande.Statut.ANNULEE: {"acheteur"},
    },
    Commande.Statut.EXPEDIEE: {
        Commande.Statut.LIVREE: {"vendeur", "livreur"},
        Commande.Statut.ECHEC_LIVRAISON: {"vendeur", "livreur"},
    },
    Commande.Statut.ECHEC_LIVRAISON: {
        Commande.Statut.ANNULEE: {"systeme", "moderateur"},
    },
    Commande.Statut.LIVREE: {
        Commande.Statut.TERMINEE: {"acheteur", "systeme"},
        Commande.Statut.LITIGE: {"acheteur"},
    },
    Commande.Statut.LITIGE: {
        Commande.Statut.TERMINEE: {"moderateur"},
        Commande.Statut.REMBOURSEE: {"moderateur"},
    },
}


def _role_transition(commande, acteur):
    """Identifie le rôle métier de l'acteur pour une commande verrouillée."""
    if acteur is None:
        return "systeme"
    if acteur.id == commande.acheteur_id:
        return "acheteur"
    if acteur.id == commande.vendeur_id:
        return "vendeur"
    if getattr(acteur, "role", None) in {"moderateur", "administrateur"}:
        return "moderateur"
    if (
        getattr(acteur, "role", None) == "livreur"
        and hasattr(commande, "livraison")
        and commande.livraison.livreur_id == acteur.id
    ):
        return "livreur"
    return None


def transitionner(commande, cible, acteur, motif=None):
    """Applique une transition autorisée, journalisée et protégée par verrou SQL."""
    with transaction.atomic():
        commande = (
            Commande.objects.select_for_update()
            # ``livraison`` est une relation inverse nullable : la joindre
            # créerait un LEFT OUTER JOIN que PostgreSQL refuse de verrouiller.
            # L'accès éventuel à la livraison est donc résolu séparément.
            .select_related("annonce")
            .get(pk=commande.pk)
        )
        autorises = TRANSITIONS_AUTORISEES.get(commande.statut, {}).get(cible, set())
        role = _role_transition(commande, acteur)
        if role not in autorises:
            raise TransitionInvalide()

        ancien_statut = commande.statut
        commande.statut = cible
        commande.save(update_fields=["statut", "updated_at"])
        HistoriqueStatutCommande.objects.create(
            commande=commande,
            ancien_statut=ancien_statut,
            nouveau_statut=cible,
            acteur=acteur,
            motif=motif or None,
        )

        # L'article est réservé à partir de sa création. Une annulation ou un
        # remboursement le remet en vente ; seule la commande terminée le vend.
        if cible in {Commande.Statut.ANNULEE, Commande.Statut.REMBOURSEE}:
            if commande.annonce.statut == Annonce.Statut.RESERVEE:
                commande.annonce.statut = Annonce.Statut.ACTIVE
                commande.annonce.save(update_fields=["statut", "updated_at"])
        elif cible == Commande.Statut.TERMINEE:
            commande.annonce.statut = Annonce.Statut.VENDUE
            commande.annonce.save(update_fields=["statut", "updated_at"])
    return commande
