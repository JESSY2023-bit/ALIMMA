"""Tests du CRUD administrateur des catégories et sous-catégories."""
import pytest

from apps.accounts.models import Utilisateur
from apps.administration.tests.test_suspension_utilisateurs import (
    connexion,
    creer_utilisateur,
    headers,
)
from apps.catalogue.models import Annonce, Categorie

URL = "/v1/admin/categories"


@pytest.fixture
def administrateur(db):
    """Crée un administrateur pour les mutations de catalogue."""
    return creer_utilisateur(
        nom="Admin ALIMMA",
        telephone="+237690000030",
        role=Utilisateur.Role.ADMINISTRATEUR,
    )


@pytest.mark.django_db
def test_visiteur_lit_l_arborescence_imbriquee(client):
    parent = Categorie.objects.create(nom="Électronique", slug="electronique")
    enfant = Categorie.objects.create(nom="Téléphones", slug="telephones", parent=parent)

    response = client.get(URL)

    assert response.status_code == 200
    assert response.json()[0]["id"] == parent.id
    assert response.json()[0]["enfants"][0]["id"] == enfant.id


@pytest.mark.django_db
def test_administrateur_cree_une_categorie_et_slug_unique(client, administrateur):
    tokens = connexion(client, administrateur)
    premier = client.post(
        URL,
        {"nom": "Maison & Jardin"},
        content_type="application/json",
        **headers(tokens),
    )
    second = client.post(
        URL,
        {"nom": "Maison & Jardin"},
        content_type="application/json",
        **headers(tokens),
    )

    assert premier.status_code == 201
    assert premier.json()["slug"] == "maison-jardin"
    assert second.status_code == 201
    assert second.json()["slug"] == "maison-jardin-2"


@pytest.mark.django_db
def test_creation_sans_nom_est_refusee(client, administrateur):
    response = client.post(
        URL,
        {},
        content_type="application/json",
        **headers(connexion(client, administrateur)),
    )

    assert response.status_code == 422


@pytest.mark.django_db
def test_creation_imbriquee_et_profondeur_excessive_refusee(client, administrateur):
    parent = Categorie.objects.create(nom="Électronique", slug="electronique")
    tokens = connexion(client, administrateur)
    enfant = client.post(
        URL,
        {"nom": "Téléphones", "parent_id": parent.id},
        content_type="application/json",
        **headers(tokens),
    )
    petit_enfant = client.post(
        URL,
        {"nom": "Smartphones", "parent_id": enfant.json()["id"]},
        content_type="application/json",
        **headers(tokens),
    )

    assert enfant.status_code == 201
    assert enfant.json()["parent_id"] == parent.id
    assert petit_enfant.status_code == 422


@pytest.mark.django_db
def test_non_administrateur_ne_peut_pas_modifier_ni_supprimer(client):
    utilisateur = creer_utilisateur(telephone="+237690000031")
    categorie = Categorie.objects.create(nom="Mode", slug="mode")
    tokens = connexion(client, utilisateur)

    modification = client.patch(
        f"{URL}/{categorie.id}",
        {"nom": "Mode femme"},
        content_type="application/json",
        **headers(tokens),
    )
    suppression = client.delete(f"{URL}/{categorie.id}", **headers(tokens))

    assert modification.status_code == 403
    assert suppression.status_code == 403


@pytest.mark.django_db
def test_categorie_ne_peut_pas_etre_son_propre_parent(client, administrateur):
    categorie = Categorie.objects.create(nom="Mode", slug="mode")

    response = client.patch(
        f"{URL}/{categorie.id}",
        {"parent_id": categorie.id},
        content_type="application/json",
        **headers(connexion(client, administrateur)),
    )

    assert response.status_code == 422


@pytest.mark.django_db
def test_suppression_bloquee_si_sous_categorie_ou_annonce(client, administrateur):
    parent = Categorie.objects.create(nom="Électronique", slug="electronique")
    categorie_annonce = Categorie.objects.create(nom="Mode", slug="mode")
    Categorie.objects.create(nom="Téléphones", slug="telephones", parent=parent)
    vendeur = creer_utilisateur(telephone="+237690000032")
    Annonce.objects.create(
        vendeur=vendeur,
        categorie=categorie_annonce,
        titre="Sac à main",
        description="Très bon état",
        prix="10000.00",
        ville="Douala",
    )
    tokens = connexion(client, administrateur)

    enfant = client.delete(f"{URL}/{parent.id}", **headers(tokens))
    annonce = client.delete(f"{URL}/{categorie_annonce.id}", **headers(tokens))

    assert enfant.status_code == 409
    assert annonce.status_code == 409
