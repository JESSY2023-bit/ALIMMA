"""Tests de l'inscription publique des utilisateurs."""
import pytest

from apps.accounts.models import Parrainage, Utilisateur

URL = "/v1/auth/inscription"


def inscription_payload(**overrides):
    """Construit une requête valide sans introduire de fixture en production."""
    payload = {
        "nom": "Alice Ngono",
        "telephone": "+237670000001",
        "email": "alice@example.cm",
        "password": "mot-de-passe-solide",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_inscription_valide_cree_un_utilisateur_bcrypt(client):
    response = client.post(URL, inscription_payload(), content_type="application/json")

    assert response.status_code == 201
    assert "password" not in response.json()
    assert "password_hash" not in response.json()
    utilisateur = Utilisateur.objects.get(telephone="+237670000001")
    assert utilisateur.role == Utilisateur.Role.UTILISATEUR
    assert len(utilisateur.code_parrainage) == 12
    assert utilisateur.password_hash.startswith("bcrypt_sha256$")
    assert utilisateur.check_password("mot-de-passe-solide")


@pytest.mark.django_db
def test_inscription_refuse_un_telephone_deja_utilise(client):
    client.post(URL, inscription_payload(), content_type="application/json")
    response = client.post(
        URL, inscription_payload(email="autre@example.cm"), content_type="application/json"
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.django_db
def test_inscription_refuse_un_email_deja_utilise(client):
    client.post(URL, inscription_payload(), content_type="application/json")
    response = client.post(
        URL, inscription_payload(telephone="+237670000002"), content_type="application/json"
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.django_db
def test_inscription_refuse_un_mot_de_passe_trop_court(client):
    response = client.post(URL, inscription_payload(password="court"), content_type="application/json")

    assert response.status_code == 422
    assert Utilisateur.objects.count() == 0


@pytest.mark.django_db
def test_inscription_refuse_un_telephone_mal_formate(client):
    response = client.post(URL, inscription_payload(telephone="+33670000000"), content_type="application/json")

    assert response.status_code == 422
    assert Utilisateur.objects.count() == 0


@pytest.mark.django_db
def test_inscription_applique_un_parrainage_valide(client):
    parrain = Utilisateur.objects.create_user(
        nom="Parrain ALIMMA", telephone="+237670000009", password="mot-de-passe-solide"
    )
    response = client.post(
        URL,
        inscription_payload(code_parrainage_utilise=parrain.code_parrainage),
        content_type="application/json",
    )

    filleul = Utilisateur.objects.get(telephone="+237670000001")
    assert response.status_code == 201
    assert filleul.parraine_par == parrain
    assert Parrainage.objects.filter(parrain=parrain, filleul=filleul).exists()


@pytest.mark.django_db
def test_inscription_ignore_un_parrainage_invalide(client):
    response = client.post(
        URL,
        inscription_payload(code_parrainage_utilise="CODEINEXIST"),
        content_type="application/json",
    )

    utilisateur = Utilisateur.objects.get(telephone="+237670000001")
    assert response.status_code == 201
    assert utilisateur.parraine_par is None
    assert not Parrainage.objects.filter(filleul=utilisateur).exists()
