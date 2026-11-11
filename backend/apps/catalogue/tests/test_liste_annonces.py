"""Tests de la liste publique paginée, triée et optimisée des annonces."""
from datetime import timedelta

import pytest
from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, AnnonceImage, Categorie


@pytest.fixture(autouse=True)
def vider_cache():
    """Évite qu'une réponse Redis d'un test n'influence le suivant."""
    cache.clear()


@pytest.fixture
def categorie(db):
    return Categorie.objects.create(nom="Maison", slug="maison")


@pytest.fixture
def vendeur(db):
    return Utilisateur.objects.create_user(
        nom="Jean Vendeur",
        telephone="+237670000081",
        password="mot-de-passe-solide",
    )


def creer_annonce(vendeur, categorie, *, statut=Annonce.Statut.ACTIVE, prix="100.00", ordre=0):
    """Crée une annonce avec relation vendeur, catégorie et image préchargeables."""
    annonce = Annonce.objects.create(
        vendeur=vendeur,
        categorie=categorie,
        titre=f"Annonce {ordre}",
        description="Description publique.",
        prix=prix,
        ville="Yaoundé",
        statut=statut,
        date_publication=timezone.now() - timedelta(minutes=ordre),
    )
    AnnonceImage.objects.create(annonce=annonce, url=f"/media/{ordre}.png", ordre=0)
    return annonce


@pytest.mark.django_db
def test_liste_anonyme_n_expose_que_les_annonces_actives(client, vendeur, categorie):
    """Les états non publics restent exclus indépendamment de tout paramètre client."""
    active = creer_annonce(vendeur, categorie, ordre=1)
    for ordre, statut in enumerate(
        (
            Annonce.Statut.EN_ATTENTE_MODERATION,
            Annonce.Statut.EN_PAUSE,
            Annonce.Statut.REJETEE,
            Annonce.Statut.VENDUE,
            Annonce.Statut.EXPIREE,
        ),
        start=2,
    ):
        creer_annonce(vendeur, categorie, statut=statut, ordre=ordre)

    response = client.get("/v1/annonces")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["data"]] == [active.id]
    assert response.json()["data"][0]["vendeur_nom"] == vendeur.nom
    assert response.json()["data"][0]["vendeur_note_moyenne"] == 0.0
    assert response.json()["data"][0]["images"] == ["/media/1.png"]


@pytest.mark.django_db
def test_liste_trie_par_prix_et_retourne_pagination(client, vendeur, categorie):
    """Les trois tris contractuels conservent la pagination attendue par le frontend."""
    premier = creer_annonce(vendeur, categorie, prix="300.00", ordre=1)
    second = creer_annonce(vendeur, categorie, prix="100.00", ordre=2)
    troisieme = creer_annonce(vendeur, categorie, prix="200.00", ordre=3)

    croissant = client.get("/v1/annonces?tri=prix_asc&par_page=2")
    decroissant = client.get("/v1/annonces?tri=prix_desc&par_page=2")

    assert [item["id"] for item in croissant.json()["data"]] == [second.id, troisieme.id]
    assert [item["id"] for item in decroissant.json()["data"]] == [premier.id, troisieme.id]
    assert croissant.json()["pagination"] == {
        "page": 1,
        "par_page": 2,
        "total": 3,
        "total_pages": 2,
    }


@pytest.mark.django_db
def test_liste_trie_par_date_et_pagine_la_seconde_page(client, vendeur, categorie):
    """Le tri par défaut est décroissant sur la publication et la page deux est accessible."""
    plus_recent = creer_annonce(vendeur, categorie, ordre=0)
    creer_annonce(vendeur, categorie, ordre=1)
    plus_ancien = creer_annonce(vendeur, categorie, ordre=2)

    premiere_page = client.get("/v1/annonces?par_page=2")
    seconde_page = client.get("/v1/annonces?par_page=2&page=2")

    assert premiere_page.json()["data"][0]["id"] == plus_recent.id
    assert seconde_page.status_code == 200
    assert [item["id"] for item in seconde_page.json()["data"]] == [plus_ancien.id]


@pytest.mark.django_db
def test_liste_applique_les_filtres_documentes_et_rejette_les_parametres_invalides(
    client, vendeur, categorie
):
    """Les filtres OpenAPI sont effectifs et leurs valeurs invalides renvoient 422."""
    cible = creer_annonce(vendeur, categorie, prix="250.00", ordre=1)
    cible.titre = "Téléphone Android"
    cible.ville = "Douala"
    cible.etat = Annonce.Etat.NEUF
    cible.save()
    autre = creer_annonce(vendeur, categorie, prix="10.00", ordre=2)
    autre.ville = "Yaoundé"
    autre.save()

    filtre = client.get(
        "/v1/annonces?q=Android&categorie_id={}&ville=Douala&prix_min=200&"
        "prix_max=300&etat=neuf&type_vente=fixe".format(categorie.id)
    )
    tri_invalide = client.get("/v1/annonces?tri=invalide")
    page_invalide = client.get("/v1/annonces?page=0")

    assert [item["id"] for item in filtre.json()["data"]] == [cible.id]
    assert tri_invalide.status_code == 422
    assert page_invalide.status_code == 422


@pytest.mark.django_db
def test_liste_n_a_pas_de_requetes_supplementaires_par_annonce(client, vendeur, categorie):
    """select_related et prefetch_related bornent les requêtes malgré plusieurs résultats."""
    for ordre in range(5):
        creer_annonce(vendeur, categorie, ordre=ordre)

    with CaptureQueriesContext(connection) as requetes:
        response = client.get("/v1/annonces?tri=prix_asc")

    assert response.status_code == 200
    # Une requête count, une pour les annonces et une pour les images.
    assert len(requetes) == 3
