"""Tests de consultation détaillée et comptage dédupliqué des annonces."""
import pytest
from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, AnnonceImage, Categorie


def auth_headers(utilisateur):
    """Crée le header Bearer associé à un compte de test."""
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(utilisateur)}"}


@pytest.fixture(autouse=True)
def vider_cache():
    """Isole les fenêtres Redis de comptage des scénarios de test."""
    cache.clear()


@pytest.fixture
def categorie(db):
    return Categorie.objects.create(nom="Mobilier", slug="mobilier-detail")


@pytest.fixture
def vendeur(db):
    return Utilisateur.objects.create_user(
        nom="Alice Vendeur",
        telephone="+237670000121",
        password="mot-de-passe-solide",
        photo_url="https://images.example.test/alice.png",
    )


def creer_annonce(vendeur, categorie, statut=Annonce.Statut.ACTIVE):
    """Crée une annonce contenant deux images volontairement non triées à l'insertion."""
    annonce = Annonce.objects.create(
        vendeur=vendeur,
        categorie=categorie,
        titre="Canapé",
        description="Canapé confortable.",
        prix="100000.00",
        ville="Yaoundé",
        statut=statut,
    )
    AnnonceImage.objects.create(annonce=annonce, url="/media/deux.png", ordre=1)
    AnnonceImage.objects.create(annonce=annonce, url="/media/un.png", ordre=0)
    return annonce


@pytest.mark.django_db
def test_detail_public_retourne_vendeur_categorie_et_images_ordonnees(client, vendeur, categorie):
    """Le détail public fournit le bloc vendeur et toutes les images dans leur ordre."""
    annonce = creer_annonce(vendeur, categorie)

    response = client.get(f"/v1/annonces/{annonce.id}")

    assert response.status_code == 200
    assert response.json()["categorie"]["id"] == categorie.id
    assert response.json()["vendeur"] == {
        "id": vendeur.id,
        "nom": vendeur.nom,
        "photo_url": vendeur.photo_url,
        "note_moyenne": 0.0,
        "nb_avis": 0,
    }
    assert response.json()["images"] == ["/media/un.png", "/media/deux.png"]


@pytest.mark.django_db
def test_compteur_est_deduplique_pendant_24_heures(client, vendeur, categorie):
    """Deux consultations de la même IP n'incrémentent qu'une seule fois le compteur."""
    annonce = creer_annonce(vendeur, categorie)

    premiere = client.get(f"/v1/annonces/{annonce.id}")
    seconde = client.get(f"/v1/annonces/{annonce.id}")

    annonce.refresh_from_db()
    assert premiere.status_code == 200
    assert seconde.status_code == 200
    assert annonce.nb_vues == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "statut_attendu"),
    [
        (None, 404),
        (Utilisateur.Role.UTILISATEUR, 404),
        (Utilisateur.Role.MODERATEUR, 200),
        (Utilisateur.Role.ADMINISTRATEUR, 200),
    ],
)
def test_annonce_non_active_est_limitee_au_proprietaire_ou_roles_autorises(
    client, vendeur, categorie, role, statut_attendu
):
    """Un visiteur est masqué tandis que modérateur et admin accèdent au contrôle."""
    annonce = creer_annonce(vendeur, categorie, statut=Annonce.Statut.EN_ATTENTE_MODERATION)
    headers = {}
    if role:
        acteur = Utilisateur.objects.create_user(
            nom=f"Acteur {role}",
            telephone={
                Utilisateur.Role.UTILISATEUR: "+237670000124",
                Utilisateur.Role.MODERATEUR: "+237670000122",
                Utilisateur.Role.ADMINISTRATEUR: "+237670000123",
            }[role],
            password="mot-de-passe-solide",
            role=role,
        )
        headers = auth_headers(acteur)

    response = client.get(f"/v1/annonces/{annonce.id}", **headers)

    assert response.status_code == statut_attendu


@pytest.mark.django_db
def test_proprietaire_peut_consulter_son_annonce_non_active(client, vendeur, categorie):
    """Le vendeur conserve l'accès à son annonce en attente de validation."""
    annonce = creer_annonce(vendeur, categorie, statut=Annonce.Statut.EN_ATTENTE_MODERATION)

    response = client.get(f"/v1/annonces/{annonce.id}", **auth_headers(vendeur))

    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_inexistant_renvoie_404(client):
    """Une identité d'annonce inexistante ne révèle aucune information interne."""
    assert client.get("/v1/annonces/999999").status_code == 404


@pytest.mark.django_db
def test_une_ip_differente_incremente_une_nouvelle_vue(client, vendeur, categorie):
    """La clé Redis varie selon l'IP, donc une seconde origine compte une vue."""
    annonce = creer_annonce(vendeur, categorie)

    client.get(f"/v1/annonces/{annonce.id}", REMOTE_ADDR="192.0.2.10")
    client.get(f"/v1/annonces/{annonce.id}", REMOTE_ADDR="192.0.2.11")

    annonce.refresh_from_db()
    assert annonce.nb_vues == 2
