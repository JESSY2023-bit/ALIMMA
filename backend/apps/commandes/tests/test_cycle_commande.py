"""Tests du cycle complet d'une commande d'achat direct."""
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, Categorie
from apps.commandes.etats import TransitionInvalide, transitionner
from apps.commandes.models import Commande, HistoriqueStatutCommande, Livraison


def headers(utilisateur):
    """Construit le Bearer token de test d'un acteur de la commande."""
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(utilisateur)}"}


@pytest.fixture
def cycle(db):
    """Crée une commande réservant une annonce et ses quatre acteurs métier."""
    vendeur = Utilisateur.objects.create_user(
        nom="Vendeur", telephone="+237670000611", password="mot-de-passe-solide"
    )
    acheteur = Utilisateur.objects.create_user(
        nom="Acheteur", telephone="+237670000612", password="mot-de-passe-solide"
    )
    livreur = Utilisateur.objects.create_user(
        nom="Livreur", telephone="+237670000613", password="mot-de-passe-solide",
        role=Utilisateur.Role.LIVREUR,
    )
    moderateur = Utilisateur.objects.create_user(
        nom="Modérateur", telephone="+237670000614", password="mot-de-passe-solide",
        role=Utilisateur.Role.MODERATEUR,
    )
    categorie = Categorie.objects.create(nom="Cycle", slug="cycle")
    annonce = Annonce.objects.create(
        vendeur=vendeur, categorie=categorie, titre="Article", description="Disponible",
        prix="10000", ville="Douala", statut=Annonce.Statut.RESERVEE,
    )
    commande = Commande.objects.create(
        acheteur=acheteur, vendeur=vendeur, annonce=annonce, quantite=1,
        montant_produit="10000", frais_livraison="0", montant_total="10000",
        mode_paiement=Commande.ModePaiement.COD, statut=Commande.Statut.ATTENTE_VENDEUR,
        mode_remise=Commande.ModeRemise.MAIN_PROPRE, ville="Douala", quartier="Akwa",
        repere="Place centrale", telephone_contact=acheteur.telephone,
    )
    Livraison.objects.create(commande=commande, livreur=livreur, qr_code="qr-cycle")
    return commande, annonce, acheteur, vendeur, livreur, moderateur


@pytest.mark.django_db
def test_transition_vendeur_autorisee_et_historisee(cycle):
    """Le vendeur accepte, puis la transition est durablement historisée."""
    commande, _, _, vendeur, _, _ = cycle

    resultat = transitionner(commande, Commande.Statut.ACCEPTEE, vendeur)

    assert resultat.statut == Commande.Statut.ACCEPTEE
    historique = HistoriqueStatutCommande.objects.get(commande=commande)
    assert historique.ancien_statut == Commande.Statut.ATTENTE_VENDEUR
    assert historique.nouveau_statut == Commande.Statut.ACCEPTEE
    assert historique.acteur == vendeur


@pytest.mark.django_db
def test_transition_refuse_role_ou_etat_invalide(cycle):
    """Un acheteur ne peut accepter, et un vendeur ne peut expédier trop tôt."""
    commande, _, acheteur, vendeur, _, _ = cycle

    with pytest.raises(TransitionInvalide):
        transitionner(commande, Commande.Statut.ACCEPTEE, acheteur)
    with pytest.raises(TransitionInvalide):
        transitionner(commande, Commande.Statut.EXPEDIEE, vendeur)


@pytest.mark.django_db
def test_annonce_reactivee_apres_annulation(cycle):
    """Refuser une commande libère l'annonce auparavant réservée."""
    commande, annonce, _, vendeur, _, _ = cycle

    transitionner(commande, Commande.Statut.ANNULEE, vendeur, "Indisponible")

    annonce.refresh_from_db()
    assert annonce.statut == Annonce.Statut.ACTIVE


@pytest.mark.django_db
def test_annonce_vendue_seulement_apres_reception(cycle):
    """L'article reste réservé pendant l'expédition, puis est vendu à la fin."""
    commande, annonce, acheteur, vendeur, _, _ = cycle
    transitionner(commande, Commande.Statut.ACCEPTEE, vendeur)
    transitionner(commande, Commande.Statut.LIVREE, vendeur)
    transitionner(commande, Commande.Statut.TERMINEE, acheteur)

    annonce.refresh_from_db()
    assert annonce.statut == Annonce.Statut.VENDUE


@pytest.mark.django_db
def test_detail_est_invisible_a_un_tiers_et_visible_a_lacheteur(client, cycle):
    """La route de détail ne révèle pas une commande aux comptes étrangers."""
    commande, _, acheteur, _, _, _ = cycle
    tiers = Utilisateur.objects.create_user(
        nom="Tiers", telephone="+237670000615", password="mot-de-passe-solide"
    )

    interdit = client.get(f"/v1/commandes/{commande.id}", **headers(tiers))
    autorise = client.get(f"/v1/commandes/{commande.id}", **headers(acheteur))

    assert interdit.status_code == 404
    assert autorise.status_code == 200
    assert autorise.json()["id"] == commande.id


@pytest.mark.django_db
def test_actions_http_exigent_le_bon_role_et_le_motif(client, cycle):
    """Le refus exige un motif, tandis que l'acceptation est réservée au vendeur."""
    commande, _, acheteur, vendeur, _, _ = cycle

    interdit = client.post(f"/v1/commandes/{commande.id}/accepter", **headers(acheteur))
    sans_motif = client.post(f"/v1/commandes/{commande.id}/refuser", **headers(vendeur))
    accepte = client.post(f"/v1/commandes/{commande.id}/accepter", **headers(vendeur))

    assert interdit.status_code == 409
    assert sans_motif.status_code == 422
    assert accepte.status_code == 200
    assert accepte.json()["statut"] == Commande.Statut.ACCEPTEE


@pytest.mark.django_db
def test_echeances_annulent_et_liberent_lannonce(cycle):
    """La commande planifiée annule les réservations dont le vendeur tarde trop."""
    commande, annonce, _, _, _, _ = cycle
    Commande.objects.filter(pk=commande.pk).update(created_at=timezone.now() - timedelta(hours=25))

    call_command("traiter_echeances_commandes")

    commande.refresh_from_db()
    annonce.refresh_from_db()
    assert commande.statut == Commande.Statut.ANNULEE
    assert annonce.statut == Annonce.Statut.ACTIVE
