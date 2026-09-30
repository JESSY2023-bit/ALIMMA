"""Tests des connexions, JWT, blacklist et limitation d'essais."""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Utilisateur
from apps.accounts.services import LoginAttemptLimiter

LOGIN_URL = "/v1/auth/login"
REFRESH_URL = "/v1/auth/refresh"
LOGOUT_URL = "/v1/auth/logout"


class FakeCache:
    """Double de Redis pour tester les limites sans dépendance réseau."""

    def __init__(self):
        self.values = {}

    def get(self, key, default=None):
        return self.values.get(key, default)

    def add(self, key, value, timeout=None):
        if key in self.values:
            return False
        self.values[key] = value
        return True

    def incr(self, key):
        self.values[key] += 1
        return self.values[key]

    def delete(self, key):
        self.values.pop(key, None)


@pytest.fixture(autouse=True)
def fake_login_cache(monkeypatch):
    """Isole chaque test du serveur Redis de développement."""
    monkeypatch.setattr("apps.accounts.services.cache", FakeCache())


@pytest.fixture
def utilisateur(db):
    """Crée un compte actif avec un mot de passe connu pour chaque scénario."""
    return Utilisateur.objects.create_user(
        nom="Alice Ngono",
        email="alice@example.cm",
        telephone="+237670000001",
        password="mot-de-passe-solide",
    )


def login(client, identifiant, password="mot-de-passe-solide"):
    """Envoie une requête de connexion JSON."""
    return client.post(
        LOGIN_URL,
        {"identifiant": identifiant, "password": password},
        content_type="application/json",
    )


def bearer_headers(access_token):
    """Construit l'en-tête JWT requis par refresh et logout selon OpenAPI."""
    return {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}


@pytest.mark.django_db
def test_connexion_par_email_emet_des_jwt(client, utilisateur):
    response = login(client, utilisateur.email)

    assert response.status_code == 200
    payload = response.json()
    access = AccessToken(payload["access_token"])
    assert payload["utilisateur"]["id"] == utilisateur.id
    assert access["id"] == utilisateur.id
    assert access["role"] == "utilisateur"
    assert access["telephone"] == utilisateur.telephone
    utilisateur.refresh_from_db()
    assert utilisateur.derniere_connexion >= timezone.now() - timedelta(seconds=5)


@pytest.mark.django_db
def test_connexion_par_telephone_emet_des_jwt(client, utilisateur):
    response = login(client, utilisateur.telephone)

    assert response.status_code == 200
    assert {"access_token", "refresh_token", "utilisateur"} <= response.json().keys()


@pytest.mark.django_db
def test_mauvais_mot_de_passe_recoit_une_erreur_generique(client, utilisateur):
    response = login(client, utilisateur.email, password="mot-de-passe-invalide")

    assert response.status_code == 401
    assert response.json()["message"] == "Identifiants invalides."


@pytest.mark.django_db
def test_compte_suspendu_ne_peut_pas_se_connecter(client, utilisateur):
    utilisateur.est_actif = False
    utilisateur.save(update_fields=["est_actif", "updated_at"])

    response = login(client, utilisateur.email)

    assert response.status_code == 401
    assert response.json()["message"] == "Identifiants invalides."


@pytest.mark.django_db
def test_refresh_valide_emet_un_nouvel_access_token(client, utilisateur):
    tokens = login(client, utilisateur.email).json()
    response = client.post(
        REFRESH_URL,
        {"refresh_token": tokens["refresh_token"]},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert AccessToken(response.json()["access_token"])["id"] == utilisateur.id
    assert response.json()["refresh_token"] == tokens["refresh_token"]


@pytest.mark.django_db
def test_refresh_sans_jwt_fonctionne(client, utilisateur):
    refresh = login(client, utilisateur.email).json()["refresh_token"]

    response = client.post(
        REFRESH_URL,
        {"refresh_token": refresh},
        content_type="application/json",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_refresh_dun_autre_utilisateur_fonctionne_sans_bearer(client, utilisateur):
    autre_utilisateur = Utilisateur.objects.create_user(
        nom="Paul Ndzi",
        email="paul@example.cm",
        telephone="+237670000002",
        password="mot-de-passe-solide",
    )
    refresh = login(client, autre_utilisateur.email).json()["refresh_token"]

    response = client.post(
        REFRESH_URL,
        {"refresh_token": refresh},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["utilisateur"]["id"] == autre_utilisateur.id


@pytest.mark.django_db
def test_refresh_revoque_ne_permet_pas_de_renouveler(client, utilisateur):
    tokens = login(client, utilisateur.email).json()
    refresh = tokens["refresh_token"]
    logout = client.post(
        LOGOUT_URL,
        {"refresh_token": refresh},
        content_type="application/json",
        **bearer_headers(tokens["access_token"]),
    )
    response = client.post(
        REFRESH_URL,
        {"refresh_token": refresh},
        content_type="application/json",
    )

    assert logout.status_code == 204
    assert response.status_code == 401
    assert set(response.json()) == {"code", "message"}


@pytest.mark.django_db
def test_logout_refuse_le_refresh_dun_autre_utilisateur(client, utilisateur):
    autre_utilisateur = Utilisateur.objects.create_user(
        nom="Paul Ndzi",
        email="paul@example.cm",
        telephone="+237670000002",
        password="mot-de-passe-solide",
    )
    tokens = login(client, utilisateur.email).json()
    refresh_autre = login(client, autre_utilisateur.email).json()["refresh_token"]

    response = client.post(
        LOGOUT_URL,
        {"refresh_token": refresh_autre},
        content_type="application/json",
        **bearer_headers(tokens["access_token"]),
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_logout_sans_jwt_est_refuse(client, utilisateur):
    refresh = login(client, utilisateur.email).json()["refresh_token"]

    response = client.post(
        LOGOUT_URL,
        {"refresh_token": refresh},
        content_type="application/json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_sixieme_echec_est_limite_pendant_quinze_minutes(client, utilisateur):
    for _ in range(LoginAttemptLimiter.maximum_attempts):
        assert login(client, utilisateur.email, password="mauvais-mot-de-passe").status_code == 401

    response = login(client, utilisateur.email)

    assert response.status_code == 401
    assert response.json()["message"] == "Identifiants invalides."
