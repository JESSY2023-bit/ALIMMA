"""Tests du changement de rôle administré et de ses profils associés."""
import pytest

from apps.accounts.models import ProfilLivreur, ProfilVendeurPro, Utilisateur
from apps.administration.models import JournalModeration

from .test_suspension_utilisateurs import connexion, creer_utilisateur, headers

URL = "/v1/admin/utilisateurs"


@pytest.fixture
def administrateur(db):
    """Crée un compte habilité à gérer les rôles."""
    return creer_utilisateur(
        nom="Admin ALIMMA",
        telephone="+237690000020",
        role=Utilisateur.Role.ADMINISTRATEUR,
    )


@pytest.fixture
def cible(db):
    """Crée un compte standard à faire évoluer."""
    return creer_utilisateur(nom="Boutique Alice", telephone="+237690000021")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        Utilisateur.Role.UTILISATEUR,
        Utilisateur.Role.MODERATEUR,
        Utilisateur.Role.ADMINISTRATEUR,
    ],
)
def test_administrateur_peut_attribuer_chaque_role_sans_profil(
    client, administrateur, cible, role
):
    response = client.patch(
        f"{URL}/{cible.id}/role",
        {"role": role},
        content_type="application/json",
        **headers(connexion(client, administrateur)),
    )

    cible.refresh_from_db()
    assert response.status_code == 200
    assert cible.role == role


@pytest.mark.django_db
def test_role_vendeur_pro_cree_un_profil_et_la_retrogradation_le_conserve(
    client, administrateur, cible
):
    tokens = connexion(client, administrateur)
    vendeur = client.patch(
        f"{URL}/{cible.id}/role",
        {"role": Utilisateur.Role.VENDEUR_PRO},
        content_type="application/json",
        **headers(tokens),
    )
    retrogradation = client.patch(
        f"{URL}/{cible.id}/role",
        {"role": Utilisateur.Role.UTILISATEUR},
        content_type="application/json",
        **headers(tokens),
    )

    profil = ProfilVendeurPro.objects.get(utilisateur=cible)
    cible.refresh_from_db()
    assert vendeur.status_code == 200
    assert profil.nom_boutique == cible.nom
    assert retrogradation.status_code == 200
    assert cible.role == Utilisateur.Role.UTILISATEUR
    assert ProfilVendeurPro.objects.filter(utilisateur=cible).exists()


@pytest.mark.django_db
def test_role_livreur_cree_son_profil_et_journalise(client, administrateur, cible):
    response = client.patch(
        f"{URL}/{cible.id}/role",
        {"role": Utilisateur.Role.LIVREUR},
        content_type="application/json",
        **headers(connexion(client, administrateur)),
    )

    assert response.status_code == 200
    assert ProfilLivreur.objects.filter(utilisateur=cible).exists()
    journal = JournalModeration.objects.filter(cible_id=cible.id).latest("id")
    assert journal.action == "utilisateur_role_modifie"
    assert "nouveau_role=livreur" in journal.details


@pytest.mark.django_db
def test_role_invalide_retourne_une_validation_422(client, administrateur, cible):
    response = client.patch(
        f"{URL}/{cible.id}/role",
        {"role": "invalide"},
        content_type="application/json",
        **headers(connexion(client, administrateur)),
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.django_db
def test_non_administrateur_ne_peut_pas_modifier_un_role(client, cible):
    response = client.patch(
        f"{URL}/{cible.id}/role",
        {"role": Utilisateur.Role.LIVREUR},
        content_type="application/json",
        **headers(connexion(client, cible)),
    )

    assert response.status_code == 403
