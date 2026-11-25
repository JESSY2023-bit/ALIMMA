"""Tests de l'administration des comptes : liste, suspension et réactivation."""
import pytest
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.accounts.models import Utilisateur
from apps.administration.models import JournalModeration

LOGIN_URL = "/v1/auth/login"
UTILISATEURS_URL = "/v1/admin/utilisateurs"
REFRESH_URL = "/v1/auth/refresh"


def creer_utilisateur(**extra_fields):
    """Construit un compte avec un téléphone unique pour les scénarios d'admin."""
    numero = extra_fields.pop("telephone", "+237690000001")
    return Utilisateur.objects.create_user(
        nom=extra_fields.pop("nom", "Compte ALIMMA"),
        telephone=numero,
        password="mot-de-passe-solide",
        **extra_fields,
    )


def connexion(client, utilisateur):
    """Retourne une paire JWT valide pour le compte fourni."""
    response = client.post(
        LOGIN_URL,
        {"identifiant": utilisateur.telephone, "password": "mot-de-passe-solide"},
        content_type="application/json",
    )
    assert response.status_code == 200
    return response.json()


def headers(tokens):
    """Construit l'en-tête Bearer d'une requête administrateur."""
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens['access_token']}"}


@pytest.fixture
def administrateur(db):
    """Crée l'administrateur habilité à gérer les comptes."""
    return creer_utilisateur(
        nom="Admin ALIMMA",
        telephone="+237690000010",
        role=Utilisateur.Role.ADMINISTRATEUR,
    )


@pytest.fixture
def utilisateur(db):
    """Crée la cible standard des actions de suspension."""
    return creer_utilisateur(
        nom="Alice Ngono",
        telephone="+237690000011",
        email="alice@example.cm",
    )


@pytest.mark.django_db
def test_un_non_administrateur_ne_peut_pas_lister_ni_suspendre(client, utilisateur):
    tokens = connexion(client, utilisateur)

    liste = client.get(UTILISATEURS_URL, **headers(tokens))
    suspension = client.post(
        f"{UTILISATEURS_URL}/{utilisateur.id}/suspendre",
        **headers(tokens),
    )

    assert liste.status_code == 403
    assert suspension.status_code == 403


@pytest.mark.django_db
def test_liste_utilisateurs_filtre_par_role_et_recherche(client, administrateur, utilisateur):
    creer_utilisateur(
        nom="Livreur Paul",
        telephone="+237690000012",
        email="paul@example.cm",
        role=Utilisateur.Role.LIVREUR,
    )
    tokens = connexion(client, administrateur)

    par_role = client.get(f"{UTILISATEURS_URL}?role=livreur", **headers(tokens))
    par_recherche = client.get(f"{UTILISATEURS_URL}?q={utilisateur.telephone}", **headers(tokens))

    assert par_role.status_code == 200
    assert par_role.json()["count"] == 1
    assert par_role.json()["results"][0]["role"] == Utilisateur.Role.LIVREUR
    assert par_recherche.status_code == 200
    assert par_recherche.json()["results"][0]["id"] == utilisateur.id


@pytest.mark.django_db
def test_suspension_blackliste_les_refresh_et_journalise(client, administrateur, utilisateur):
    tokens_utilisateur = connexion(client, utilisateur)
    tokens_admin = connexion(client, administrateur)

    response = client.post(
        f"{UTILISATEURS_URL}/{utilisateur.id}/suspendre",
        **headers(tokens_admin),
    )
    refresh = client.post(
        REFRESH_URL,
        {"refresh_token": tokens_utilisateur["refresh_token"]},
        content_type="application/json",
    )
    profil = client.get("/v1/utilisateurs/moi", **headers(tokens_utilisateur))

    utilisateur.refresh_from_db()
    assert response.status_code == 200
    assert response.json()["est_actif"] is False
    assert utilisateur.est_actif is False
    assert BlacklistedToken.objects.filter(
        token__in=OutstandingToken.objects.filter(user=utilisateur)
    ).exists()
    assert refresh.status_code == 401
    assert profil.status_code == 401
    journal = JournalModeration.objects.get(cible_id=utilisateur.id)
    assert journal.moderateur == administrateur
    assert journal.action == "utilisateur_suspendu"
    assert journal.cible_type == "utilisateur"


@pytest.mark.django_db
def test_reactivation_bascule_le_compte_et_journalise(client, administrateur, utilisateur):
    utilisateur.est_actif = False
    utilisateur.save(update_fields=["est_actif", "updated_at"])
    tokens_admin = connexion(client, administrateur)

    response = client.post(
        f"{UTILISATEURS_URL}/{utilisateur.id}/suspendre",
        **headers(tokens_admin),
    )

    utilisateur.refresh_from_db()
    assert response.status_code == 200
    assert utilisateur.est_actif is True
    assert JournalModeration.objects.filter(
        moderateur=administrateur,
        cible_id=utilisateur.id,
        action="utilisateur_reactive",
    ).exists()


@pytest.mark.django_db
def test_administrateur_ne_peut_pas_se_suspendre(client, administrateur):
    tokens = connexion(client, administrateur)

    response = client.post(
        f"{UTILISATEURS_URL}/{administrateur.id}/suspendre",
        **headers(tokens),
    )

    administrateur.refresh_from_db()
    assert response.status_code == 403
    assert administrateur.est_actif is True
    assert not JournalModeration.objects.filter(cible_id=administrateur.id).exists()
