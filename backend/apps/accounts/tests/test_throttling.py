"""Tests des quotas d'inscription et de connexion publics."""
import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def vider_cache():
    """Isole les compteurs Redis DRF entre les scénarios de cette suite."""
    cache.clear()
    yield
    cache.clear()


def inscription_payload(numero):
    """Construit un compte valide distinct pour compter seulement le quota."""
    return {
        "nom": "Utilisateur Limité",
        "telephone": f"+237670000{numero:03d}",
        "email": f"limite-{numero}@example.cm",
        "password": "mot-de-passe-solide",
    }


@pytest.mark.django_db
def test_inscription_est_limitee_apres_cinq_requetes(client):
    """La sixième inscription de la même IP retourne l'erreur normalisée."""
    for numero in range(1, 6):
        response = client.post(
            "/v1/auth/inscription",
            inscription_payload(numero),
            content_type="application/json",
        )
        assert response.status_code == 201

    response = client.post(
        "/v1/auth/inscription",
        inscription_payload(6),
        content_type="application/json",
    )

    assert response.status_code == 429
    assert response.json()["code"] == "RATE_LIMITED"


@pytest.mark.django_db
def test_login_est_limite_apres_dix_requetes(client):
    """Le quota login complète le limiteur d'échecs par identifiant existant."""
    payload = {"identifiant": "inconnu@example.cm", "password": "mot-de-passe-solide"}
    for _ in range(10):
        response = client.post("/v1/auth/login", payload, content_type="application/json")
        assert response.status_code == 401

    response = client.post("/v1/auth/login", payload, content_type="application/json")

    assert response.status_code == 429
    assert response.json()["code"] == "RATE_LIMITED"
