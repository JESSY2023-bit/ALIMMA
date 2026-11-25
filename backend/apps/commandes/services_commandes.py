"""Services transactionnels de création de commande."""
import secrets
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException, NotFound, ValidationError

from apps.catalogue.models import Annonce

from .models import CodePromo, Commande, Livraison, Paiement
from .services import frais_livraison


class ConflitCommande(APIException):
    """Empêche la commande d'une annonce devenue indisponible entre deux achats."""

    status_code = 409
    default_code = "CONFLICT"
    default_detail = "Cette annonce n'est plus disponible à la commande."


class PaiementMobileMoneyNonDisponible(APIException):
    """Indique que le canal Mobile Money n'est pas encore intégré au MVP."""

    status_code = 501
    default_code = "NOT_IMPLEMENTED"
    default_detail = "Le paiement Mobile Money n'est pas encore disponible."


def _generer_qr_code():
    """Produit un identifiant opaque de livraison sous la limite de 64 caractères."""
    return secrets.token_urlsafe(32)


def _appliquer_promotion(code, vendeur, montant_produit):
    """Verrouille et applique un code valide, ou retourne un message explicite.

    Le schéma de référence ne prévoit pas de colonne d'historique pour le
    code promo : le champ ``code_parrainage_utilise`` reste réservé au
    parrainage et ne reçoit donc jamais ce code de trente caractères.
    """
    if not code:
        return montant_produit, None, None

    try:
        promo = CodePromo.objects.select_for_update().get(code__iexact=code)
    except CodePromo.DoesNotExist:
        return montant_produit, None, "Le code promo est invalide et a été ignoré."

    maintenant = timezone.now()
    invalide = (
        not promo.est_actif
        or promo.date_debut > maintenant
        or promo.date_fin < maintenant
        or (promo.usage_max is not None and promo.usage_actuel >= promo.usage_max)
        or (promo.type == CodePromo.Type.BOUTIQUE and promo.vendeur_id != vendeur.id)
    )
    if invalide:
        return montant_produit, None, "Le code promo n'est plus applicable et a été ignoré."

    if promo.reduction_pct is not None:
        reduction = montant_produit * promo.reduction_pct / Decimal("100")
    elif promo.reduction_montant is not None:
        reduction = promo.reduction_montant
    else:
        return (
            montant_produit,
            None,
            "Le code promo ne contient aucune réduction et a été ignoré.",
        )

    promo.usage_actuel += 1
    promo.save(update_fields=["usage_actuel"])
    # Le schéma cible ne prévoit aucun historique de code promo. Le champ
    # ``code_parrainage_utilise`` reste réservé au parrainage (12 caractères).
    return max(montant_produit - reduction, Decimal("0")), None, None


def creer_commande(*, acheteur, donnees):
    """Crée atomiquement la commande COD, son paiement et sa livraison.

    L'annonce est verrouillée avant toute écriture. Deux transactions qui la
    ciblent ne peuvent donc pas confirmer le même article simultanément.
    """
    if donnees["mode_paiement"] == Commande.ModePaiement.MOBILE_MONEY:
        raise PaiementMobileMoneyNonDisponible()

    # Le serializer injecte cette valeur pour l'API. La valeur par défaut est
    # répétée ici afin que le service reste sûr lorsqu'il est appelé en tâche
    # de fond ou dans un test transactionnel.
    quantite = donnees.get("quantite", 1)

    with transaction.atomic():
        try:
            annonce = Annonce.objects.select_for_update().get(pk=donnees["annonce_id"])
        except Annonce.DoesNotExist as exc:
            raise NotFound("Cette annonce n'existe pas.") from exc

        if annonce.statut != Annonce.Statut.ACTIVE:
            raise ConflitCommande()
        if annonce.vendeur_id == acheteur.id:
            raise ValidationError("Vous ne pouvez pas commander votre propre annonce.")

        montant_produit = annonce.prix * quantite
        montant_reduit, code_applique, message = _appliquer_promotion(
            donnees.get("code_promo"), annonce.vendeur, montant_produit
        )
        frais = frais_livraison()
        commande = Commande.objects.create(
            acheteur=acheteur,
            annonce=annonce,
            vendeur=annonce.vendeur,
            quantite=quantite,
            montant_produit=montant_produit,
            frais_livraison=frais,
            montant_total=montant_reduit + frais,
            mode_paiement=Commande.ModePaiement.COD,
            statut=Commande.Statut.CONFIRMEE,
            adresse_livraison=donnees["adresse_livraison"],
            ville_livraison=donnees["ville_livraison"],
            code_parrainage_utilise=code_applique,
        )
        Paiement.objects.create(
            commande=commande,
            methode=Commande.ModePaiement.COD,
            montant=commande.montant_total,
            statut=Paiement.Statut.EN_ATTENTE,
        )
        Livraison.objects.create(commande=commande, qr_code=_generer_qr_code())

        annonce.statut = Annonce.Statut.VENDUE
        annonce.save(update_fields=["statut", "updated_at"])

    return commande, message
