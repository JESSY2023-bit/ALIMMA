"""Tests de recherche textuelle, filtres et géolocalisation du catalogue."""
from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, Categorie


@pytest.fixture(autouse=True)
def vider_cache():
    """Isole les résultats publics mémorisés entre les scénarios."""
    cache.clear()


@pytest.fixture
def vendeur(db):
    """Crée le vendeur des annonces de recherche."""
    return Utilisateur.objects.create_user(
        nom="Vendeur recherche",
        telephone="+237670000301",
        password="mot-de-passe-solide",
    )


@pytest.fixture
def categories(db):
    """Construit une catégorie parente et deux sous-catégories."""
    parent = Categorie.objects.create(nom="Téléphonie", slug="telephonie")
    enfant = Categorie.objects.create(nom="Smartphones", slug="smartphones", parent=parent)
    autre = Categorie.objects.create(nom="Informatique", slug="informatique")
    return parent, enfant, autre


def creer_annonce(vendeur, categorie, *, titre, **champs):
    """Crée une annonce active avec des valeurs adaptées aux filtres publics."""
    valeurs = {
        "description": "Description de produit disponible.",
        "prix": "100.00",
        "ville": "Douala",
        "etat": Annonce.Etat.OCCASION,
        "type_vente": Annonce.TypeVente.FIXE,
        "statut": Annonce.Statut.ACTIVE,
        "date_publication": timezone.now() - timedelta(minutes=1),
    }
    valeurs.update(champs)
    return Annonce.objects.create(
        vendeur=vendeur,
        categorie=categorie,
        titre=titre,
        **valeurs,
    )


@pytest.mark.django_db
def test_recherche_par_mot_cle_et_tolerance_aux_fautes(client, vendeur, categories):
    """Le titre est recherché exactement et avec une faute de frappe proche."""
    _, smartphones, autre = categories
    iphone = creer_annonce(vendeur, smartphones, titre="iPhone 15 Pro")
    description = creer_annonce(
        vendeur,
        autre,
        titre="Ordinateur portable",
        description="Chaise",
    )

    exacte = client.get("/v1/annonces?q=iPhone")
    approximative = client.get("/v1/annonces?q=iphon")
    description_approximative = client.get("/v1/annonces?q=chaisse")

    assert [item["id"] for item in exacte.json()["data"]] == [iphone.id]
    assert [item["id"] for item in approximative.json()["data"]] == [iphone.id]
    assert [item["id"] for item in description_approximative.json()["data"]] == [description.id]


@pytest.mark.django_db
def test_filtres_isoles_et_combines(client, vendeur, categories):
    """Chaque filtre, puis leur intersection, ne laisse passer que la cible."""
    _, smartphones, _ = categories
    cible = creer_annonce(
        vendeur,
        smartphones,
        titre="Samsung Galaxy neuf",
        prix="300.00",
        ville="Yaoundé",
        etat=Annonce.Etat.NEUF,
        type_vente=Annonce.TypeVente.ENCHERE,
    )
    creer_annonce(vendeur, smartphones, titre="Samsung occasion", prix="20.00")

    for parametre, valeur in (
        ("ville", "Yaoundé"),
        ("prix_min", "250"),
        ("prix_max", "350"),
        ("etat", "neuf"),
        ("type_vente", "enchere"),
    ):
        response = client.get(f"/v1/annonces?{parametre}={valeur}")
        assert cible.id in [item["id"] for item in response.json()["data"]]

    response = client.get(
        f"/v1/annonces?q=Galaxy&categorie_id={smartphones.id}&ville=Yaoundé&"
        "prix_min=250&prix_max=350&etat=neuf&type_vente=enchere"
    )
    assert [item["id"] for item in response.json()["data"]] == [cible.id]


@pytest.mark.django_db
def test_categorie_parente_inclut_les_annonces_de_ses_enfants(client, vendeur, categories):
    """Un filtre parent remonte les annonces rattachées aux sous-catégories."""
    parent, smartphones, autre = categories
    enfant = creer_annonce(vendeur, smartphones, titre="Téléphone enfant")
    creer_annonce(vendeur, autre, titre="Ordinateur hors catégorie")

    response = client.get(f"/v1/annonces?categorie_id={parent.id}")

    assert [item["id"] for item in response.json()["data"]] == [enfant.id]


@pytest.mark.django_db
def test_annonces_non_actives_sont_exclues_de_la_recherche(client, vendeur, categories):
    """Le filtre de statut public ne peut pas être contourné par le texte recherché."""
    _, smartphones, _ = categories
    active = creer_annonce(vendeur, smartphones, titre="iPhone public")
    creer_annonce(
        vendeur,
        smartphones,
        titre="iPhone privé",
        statut=Annonce.Statut.EN_PAUSE,
    )

    response = client.get("/v1/annonces?q=iPhone")

    assert [item["id"] for item in response.json()["data"]] == [active.id]


@pytest.mark.django_db
def test_recherche_carte_respecte_le_rayon_et_le_statut(client, vendeur, categories):
    """ST_DWithin renvoie les annonces actives dans le rayon demandé seulement."""
    _, smartphones, _ = categories
    proche = creer_annonce(
        vendeur,
        smartphones,
        titre="Annonce proche",
        latitude="4.051100",
        longitude="9.767900",
        localisation="SRID=4326;POINT(9.767900 4.051100)",
    )
    creer_annonce(
        vendeur,
        smartphones,
        titre="Annonce lointaine",
        latitude="4.151100",
        longitude="9.867900",
        localisation="SRID=4326;POINT(9.867900 4.151100)",
    )
    creer_annonce(
        vendeur,
        smartphones,
        titre="Annonce en pause",
        statut=Annonce.Statut.EN_PAUSE,
        latitude="4.051200",
        longitude="9.768000",
        localisation="SRID=4326;POINT(9.768000 4.051200)",
    )

    dans_rayon = client.get("/v1/annonces/carte?lat=4.051000&lng=9.768000&rayon_km=2")
    hors_rayon = client.get("/v1/annonces/carte?lat=4.051000&lng=9.768000&rayon_km=0.01")

    assert [item["id"] for item in dans_rayon.json()] == [proche.id]
    assert hors_rayon.json() == []


@pytest.mark.django_db
def test_recherche_carte_valide_ses_coordonnees(client):
    """Les coordonnées incomplètes ou un rayon excessif produisent une 422."""
    assert client.get("/v1/annonces/carte?lat=4.05").status_code == 422
    assert client.get("/v1/annonces/carte?lat=4.05&lng=9.76&rayon_km=101").status_code == 422
    assert client.get("/v1/annonces/carte?lat=91&lng=9.76").status_code == 422


@pytest.mark.django_db
def test_recherche_rejette_les_filtres_incoherents(client, vendeur, categories):
    """Les valeurs invalides ne sont jamais transformées en recherche ambiguë."""
    _, smartphones, _ = categories
    creer_annonce(vendeur, smartphones, titre="Annonce test")

    reponses = (
        client.get("/v1/annonces?categorie_id=999999"),
        client.get("/v1/annonces?etat=invalide"),
        client.get("/v1/annonces?type_vente=invalide"),
        client.get("/v1/annonces?prix_min=abc"),
        client.get("/v1/annonces?prix_min=500&prix_max=100"),
    )

    for response in reponses:
        assert response.status_code == 422
