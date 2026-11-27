"""Tests du parcours OTP de vérification et de réinitialisation."""
from unittest.mock import patch

import pytest
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Utilisateur
from apps.accounts.services import OtpService
from apps.catalogue.models import Categorie


def stocker_code(telephone, code, objectif):
    """Prépare un OTP connu sans jamais enregistrer son contenu en clair."""
    cache.set(
        OtpService._cle(telephone, objectif),
        {"hash": OtpService._empreinte(code), "essais": 0},
        timeout=OtpService.DUREES[objectif],
    )


@pytest.mark.django_db
def test_inscription_exige_otp_et_verification_permet_la_connexion(client):
    """Le compte public reste sans JWT jusqu'à la validation du téléphone."""
    with patch("apps.accounts.views.OtpService.envoyer") as envoyer:
        inscription = client.post(
            "/v1/auth/inscription",
            {"nom": "Alice OTP", "telephone": "+237670007001", "password": "mot-de-passe-solide"},
            content_type="application/json",
        )

    utilisateur = Utilisateur.objects.get(telephone="+237670007001")
    assert inscription.status_code == 201
    assert inscription.json()["otp_requis"] is True
    assert utilisateur.telephone_verifie is False
    envoyer.assert_called_once_with(utilisateur, OtpService.INSCRIPTION)

    avant = client.post(
        "/v1/auth/login",
        {"identifiant": utilisateur.telephone, "password": "mot-de-passe-solide"},
        content_type="application/json",
    )
    stocker_code(utilisateur.telephone, "123456", OtpService.INSCRIPTION)
    verification = client.post(
        "/v1/auth/verify-otp",
        {"telephone": utilisateur.telephone, "code": "123456"},
        content_type="application/json",
    )
    apres = client.post(
        "/v1/auth/login",
        {"identifiant": utilisateur.telephone, "password": "mot-de-passe-solide"},
        content_type="application/json",
    )

    assert avant.status_code == 401
    assert verification.status_code == 200
    assert apres.status_code == 200
    assert "access_token" in apres.json()


@pytest.mark.django_db
def test_otp_faux_expire_et_quatrieme_essai_sont_refuses(client):
    """Le code ne survit ni à l'expiration ni à plus de trois essais."""
    utilisateur = Utilisateur.objects.create_user(
        nom="Bob OTP", telephone="+237670007002", password="mot-de-passe-solide",
        telephone_verifie=False,
    )
    stocker_code(utilisateur.telephone, "111111", OtpService.INSCRIPTION)
    for _ in range(3):
        reponse = client.post(
            "/v1/auth/verify-otp",
            {"telephone": utilisateur.telephone, "code": "999999"},
            content_type="application/json",
        )
        assert reponse.status_code == 401
    bloque = client.post(
        "/v1/auth/verify-otp",
        {"telephone": utilisateur.telephone, "code": "111111"},
        content_type="application/json",
    )
    cache.delete(OtpService._cle(utilisateur.telephone, OtpService.INSCRIPTION))
    expire = client.post(
        "/v1/auth/verify-otp",
        {"telephone": utilisateur.telephone, "code": "111111"},
        content_type="application/json",
    )

    assert bloque.status_code == 401
    assert expire.status_code == 401


@pytest.mark.django_db
def test_renvoi_otp_est_limite_par_telephone(client):
    """Le scope otp bloque les renvois successifs du même numéro."""
    utilisateur = Utilisateur.objects.create_user(
        nom="Charly OTP", telephone="+237670007003", password="mot-de-passe-solide",
        telephone_verifie=False,
    )
    with patch("apps.accounts.views.OtpService.envoyer"):
        reponses = [
            client.post(
                "/v1/auth/renvoyer-otp",
                {"telephone": utilisateur.telephone},
                content_type="application/json",
            )
            for _ in range(4)
        ]
    assert [reponse.status_code for reponse in reponses[:3]] == [200, 200, 200]
    assert reponses[3].status_code == 429
    assert reponses[3].json()["code"] == "RATE_LIMITED"


@pytest.mark.django_db
def test_mot_de_passe_oublie_n_enumere_pas_les_comptes(client):
    """Le même message est retourné pour un numéro enregistré ou inconnu."""
    utilisateur = Utilisateur.objects.create_user(
        nom="Diane OTP", telephone="+237670007004", password="mot-de-passe-solide"
    )
    with patch("apps.accounts.views.OtpService.envoyer"):
        connu = client.post(
            "/v1/auth/mot-de-passe-oublie", {"telephone": utilisateur.telephone},
            content_type="application/json",
        )
        inconnu = client.post(
            "/v1/auth/mot-de-passe-oublie", {"telephone": "+237670007099"},
            content_type="application/json",
        )
    assert connu.status_code == inconnu.status_code == 200
    assert connu.json() == inconnu.json()


@pytest.mark.django_db
def test_reinitialisation_revoque_les_refresh_tokens(client):
    """Un reset valide change le secret et blackliste les sessions existantes."""
    utilisateur = Utilisateur.objects.create_user(
        nom="Emma OTP", telephone="+237670007005", password="mot-de-passe-solide"
    )
    refresh = str(RefreshToken.for_user(utilisateur))
    stocker_code(utilisateur.telephone, "222222", OtpService.REINITIALISATION)
    verification = client.post(
        "/v1/auth/mot-de-passe-oublie/verifier",
        {"telephone": utilisateur.telephone, "code": "222222"},
        content_type="application/json",
    )
    reset = client.post(
        "/v1/auth/mot-de-passe-oublie/reinitialiser",
        {
            "reset_token": verification.json()["reset_token"],
            "password": "nouveau-secret-solide",
        },
        content_type="application/json",
    )
    ancien_refresh = client.post(
        "/v1/auth/refresh",
        {"refresh_token": refresh},
        content_type="application/json",
    )

    utilisateur.refresh_from_db()
    assert reset.status_code == 204
    assert utilisateur.check_password("nouveau-secret-solide")
    assert ancien_refresh.status_code == 401


@pytest.mark.django_db
def test_publication_refusee_si_telephone_non_verifie(client):
    """Une authentification JWT ne suffit pas sans preuve OTP du téléphone."""
    utilisateur = Utilisateur.objects.create_user(
        nom="Fred OTP", telephone="+237670007006", password="mot-de-passe-solide",
        telephone_verifie=False,
    )
    categorie = Categorie.objects.create(nom="OTP", slug="otp-publication")
    refresh = RefreshToken.for_user(utilisateur)
    reponse = client.post(
        "/v1/annonces",
        {
            "categorie_id": categorie.id,
            "titre": "Objet",
            "description": "Description",
            "prix": 1000,
        },
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )

    assert reponse.status_code == 403
    assert reponse.json()["code"] == "PHONE_NOT_VERIFIED"
