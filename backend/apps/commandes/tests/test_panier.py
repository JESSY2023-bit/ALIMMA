"""Tests du panier Redis et de son recalcul depuis les annonces."""
import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, Categorie
from apps.commandes.models import ParametreSite


class FauxCache:
    """Double Redis minimal pour vérifier les contenus et les expirations demandées."""

    def __init__(self):
        self.valeurs = {}
        self.timeouts = {}

    def get(self, cle, defaut=None):
        return self.valeurs.get(cle, defaut)

    def set(self, cle, valeur, timeout=None):
        self.valeurs[cle] = valeur
        self.timeouts[cle] = timeout

    def delete(self, cle):
        self.valeurs.pop(cle, None)
        self.timeouts.pop(cle, None)


@pytest.fixture(autouse=True)
def faux_cache(monkeypatch):
    """Évite une dépendance Redis réseau pour les scénarios unitaires du panier."""
    cache = FauxCache()
    monkeypatch.setattr("apps.commandes.services.cache", cache)
    return cache


def headers(utilisateur):
    """Construit le header JWT du client authentifié."""
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(utilisateur)}"}


@pytest.fixture
def utilisateurs(db):
    """Crée séparément le vendeur et l'acheteur des scénarios."""
    vendeur = Utilisateur.objects.create_user(
        nom="Vendeur", telephone="+237670000401", password="mot-de-passe-solide"
    )
    acheteur = Utilisateur.objects.create_user(
        nom="Acheteur", telephone="+237670000402", password="mot-de-passe-solide"
    )
    return vendeur, acheteur


@pytest.fixture
def annonce(db, utilisateurs):
    """Fournit une annonce active avec un prix qui sera toujours relu en base."""
    categorie = Categorie.objects.create(nom="Maison panier", slug="maison-panier")
    return Annonce.objects.create(
        vendeur=utilisateurs[0],
        categorie=categorie,
        titre="Téléphone panier",
        description="Annonce disponible.",
        prix="1500.00",
        ville="Douala",
        statut=Annonce.Statut.ACTIVE,
    )


@pytest.mark.django_db
def test_ajout_recalcul_des_prix_et_expiration(client, utilisateurs, annonce, faux_cache):
    """L'ajout conserve seulement quantité/id et applique les frais configurés."""
    ParametreSite.objects.create(cle="frais_livraison_defaut", valeur="250.00")

    response = client.post(
        "/v1/panier/articles",
        {"annonce_id": annonce.id, "quantite": 2, "prix": "1"},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )

    assert response.status_code == 200
    assert response.json()["articles"][0]["prix_unitaire"] == 1500.0
    assert response.json()["sous_total"] == 3000.0
    assert response.json()["frais_livraison"] == 250.0
    assert response.json()["total"] == 3250.0
    assert faux_cache.valeurs[f"panier:{utilisateurs[1].id}"] == {str(annonce.id): 2}
    assert faux_cache.timeouts[f"panier:{utilisateurs[1].id}"] == 7 * 24 * 60 * 60


@pytest.mark.django_db
def test_modifier_retirer_et_vider_le_panier(client, utilisateurs, annonce):
    """Les opérations de ligne affectent seulement le panier de l'acheteur connecté."""
    client.post(
        "/v1/panier/articles",
        {"annonce_id": annonce.id, "quantite": 1},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )
    modification = client.patch(
        f"/v1/panier/articles/{annonce.id}",
        {"quantite": 3},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )
    retrait = client.delete(f"/v1/panier/articles/{annonce.id}", **headers(utilisateurs[1]))
    vidage = client.delete("/v1/panier", **headers(utilisateurs[1]))

    assert modification.json()["articles"][0]["quantite"] == 3
    assert retrait.status_code == 204
    assert vidage.status_code == 204


@pytest.mark.django_db
def test_annonce_inactive_est_retirée_a_la_lecture(client, utilisateurs, annonce):
    """Une annonce vendue disparaît automatiquement du panier suivant."""
    client.post(
        "/v1/panier/articles",
        {"annonce_id": annonce.id, "quantite": 1},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )
    annonce.statut = Annonce.Statut.VENDUE
    annonce.save(update_fields=["statut", "updated_at"])

    response = client.get("/v1/panier", **headers(utilisateurs[1]))

    assert response.status_code == 200
    assert response.json()["articles"] == []
    assert "retirées" in response.json()["message"]


@pytest.mark.django_db
def test_panier_refuse_propre_annonce_quantite_invalide_et_anonyme(client, utilisateurs, annonce):
    """Les protections métier et JWT couvrent les entrées non autorisées."""
    propre = client.post(
        "/v1/panier/articles",
        {"annonce_id": annonce.id, "quantite": 1},
        content_type="application/json",
        **headers(utilisateurs[0]),
    )
    invalide = client.post(
        "/v1/panier/articles",
        {"annonce_id": annonce.id, "quantite": 0},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )
    anonyme = client.get("/v1/panier")

    assert propre.status_code == 422
    assert invalide.status_code == 422
    assert anonyme.status_code == 401
    assert set(invalide.json()) == {"code", "message"}


@pytest.mark.django_db
def test_panier_recalcule_prix_apres_nouveau_jwt(client, utilisateurs, annonce):
    """Le panier Redis est retrouvé et son prix est relu après une reconnexion."""
    client.post(
        "/v1/panier/articles",
        {"annonce_id": annonce.id, "quantite": 1},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )
    annonce.prix = "1750.00"
    annonce.save(update_fields=["prix", "updated_at"])

    response = client.get("/v1/panier", **headers(utilisateurs[1]))

    assert response.status_code == 200
    assert response.json()["articles"][0]["prix_unitaire"] == 1750.0


@pytest.mark.django_db
def test_panier_refuse_annonce_inactive_et_ligne_absente(client, utilisateurs, annonce):
    """Une annonce inactive ou une ligne inconnue renvoie une erreur normalisée."""
    annonce.statut = Annonce.Statut.EN_PAUSE
    annonce.save(update_fields=["statut", "updated_at"])

    ajout_inactif = client.post(
        "/v1/panier/articles",
        {"annonce_id": annonce.id, "quantite": 1},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )
    quantite_invalide = client.patch(
        f"/v1/panier/articles/{annonce.id}",
        {"quantite": 0},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )
    modification_absente = client.patch(
        f"/v1/panier/articles/{annonce.id}",
        {"quantite": 1},
        content_type="application/json",
        **headers(utilisateurs[1]),
    )
    retrait_absent = client.delete(
        f"/v1/panier/articles/{annonce.id}", **headers(utilisateurs[1])
    )

    assert ajout_inactif.status_code == 404
    assert quantite_invalide.status_code == 422
    assert modification_absente.status_code == 404
    assert retrait_absent.status_code == 404
