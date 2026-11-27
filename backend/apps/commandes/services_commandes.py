"""Services transactionnels de création de commande."""
import secrets
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException, NotFound, ValidationError

from apps.catalogue.models import Annonce
from config.money import fcfa

from .models import CodePromo, Commande, Livraison, Paiement
from .services import frais_livraison


class ConflitCommande(APIException):
    """Empêche la commande d'une annonce devenue indisponible entre deux achats."""

    status_code = 409
    default_code = "CONFLICT"
    default_detail = "Cette annonce n'est plus disponible à la commande."


def _generer_qr_code():
    """Produit un identifiant opaque de livraison sous la limite de 64 caractères."""
    return secrets.token_urlsafe(32)


def _appliquer_promotion(code, vendeur, montant_produit):
    """Retourne la réduction FCFA, le code appliqué et un éventuel message."""
    if not code:
        return 0, None, None

    try:
        promo = CodePromo.objects.select_for_update().get(code__iexact=code)
    except CodePromo.DoesNotExist:
        return 0, None, "Le code promo est invalide et a été ignoré."

    maintenant = timezone.now()
    invalide = (
        not promo.est_actif
        or promo.date_debut > maintenant
        or promo.date_fin < maintenant
        or (promo.usage_max is not None and promo.usage_actuel >= promo.usage_max)
        or (promo.type == CodePromo.Type.BOUTIQUE and promo.vendeur_id != vendeur.id)
    )
    if invalide:
        return 0, None, "Le code promo n'est plus applicable et a été ignoré."

    if promo.reduction_pct is not None:
        reduction = fcfa(Decimal(montant_produit) * promo.reduction_pct / Decimal("100"))
    elif promo.reduction_montant is not None:
        reduction = fcfa(promo.reduction_montant)
    else:
        return (
            0,
            None,
            "Le code promo ne contient aucune réduction et a été ignoré.",
        )

    promo.usage_actuel += 1
    promo.save(update_fields=["usage_actuel"])
    # Une promotion ne peut jamais dépasser le prix brut de l'article.
    return min(reduction, montant_produit), promo, None


def creer_commande(*, acheteur, donnees):
    """Crée atomiquement une commande directe, son paiement et sa livraison.

    L'annonce est verrouillée avant toute écriture. Deux transactions qui la
    ciblent ne peuvent donc pas confirmer le même article simultanément.
    """
    with transaction.atomic():
        try:
            annonce = Annonce.objects.select_for_update().get(pk=donnees["annonce_id"])
        except Annonce.DoesNotExist as exc:
            raise NotFound("Cette annonce n'existe pas.") from exc

        if annonce.statut != Annonce.Statut.ACTIVE:
            raise ConflitCommande()
        if annonce.vendeur_id == acheteur.id:
            raise ValidationError("Vous ne pouvez pas commander votre propre annonce.")

        # Une annonce est un objet unique : quantité et multiplication du prix
        # sont volontairement absentes du flux d'achat direct.
        montant_produit = fcfa(annonce.prix)
        montant_reduction, code_promo, message = _appliquer_promotion(
            donnees.get("code_promo"), annonce.vendeur, montant_produit
        )
        frais = fcfa(frais_livraison())
        commande = Commande.objects.create(
            acheteur=acheteur,
            annonce=annonce,
            vendeur=annonce.vendeur,
            quantite=1,
            montant_produit=montant_produit,
            montant_reduction=montant_reduction,
            frais_livraison=frais,
            montant_total=montant_produit - montant_reduction + frais,
            code_promo=code_promo,
            mode_paiement=donnees["mode_paiement"],
            statut=(
                Commande.Statut.ATTENTE_PAIEMENT
                if donnees["mode_paiement"] == Commande.ModePaiement.MOBILE_MONEY
                else Commande.Statut.ATTENTE_VENDEUR
            ),
            mode_remise=donnees["mode_remise"],
            ville=donnees["ville"],
            quartier=donnees["quartier"],
            repere=donnees["repere"],
            latitude=donnees.get("latitude"),
            longitude=donnees.get("longitude"),
            telephone_contact=donnees["telephone_contact"],
        )
        Paiement.objects.create(
            commande=commande,
            methode=donnees["mode_paiement"],
            operateur=donnees.get("operateur"),
            montant=commande.montant_total,
            statut=Paiement.Statut.EN_ATTENTE,
        )
        Livraison.objects.create(commande=commande, qr_code=_generer_qr_code())

        annonce.statut = Annonce.Statut.RESERVEE
        annonce.save(update_fields=["statut", "updated_at"])

    return commande, message
