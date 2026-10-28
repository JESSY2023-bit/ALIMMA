"""Tests de publication multipart des annonces soumises à la modération."""
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, Categorie

URL = "/v1/annonces"


def image_valide(nom="produit.png"):
    """Produit une petite image PNG réellement lisible par Pillow."""
    output = BytesIO()
    Image.new("RGB", (2, 2), color="white").save(output, format="PNG")
    return SimpleUploadedFile(nom, output.getvalue(), content_type="image/png")


@pytest.fixture
def vendeur(db):
    """Crée le propriétaire déduit exclusivement du JWT de publication."""
    return Utilisateur.objects.create_user(
        nom="Alice Ngono",
        telephone="+237670000051",
        password="mot-de-passe-solide",
    )


@pytest.fixture
def categorie(db):
    """Crée une catégorie existante et utilisable dans les requêtes multipart."""
    return Categorie.objects.create(nom="Téléphones", slug="telephones")


def auth_headers(utilisateur):
    """Construit l'authentification Bearer minimale pour la publication."""
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(utilisateur)}"}


def donnees_annonce(categorie, **overrides):
    """Construit une publication valide, modifiable selon le scénario testé."""
    data = {
        "titre": "iPhone 13",
        "description": "Téléphone en excellent état avec chargeur.",
        "prix": "250000.00",
        "categorie_id": categorie.id,
        "ville": "Douala",
        "etat": "occasion",
        "type_vente": "fixe",
        "images": [image_valide()],
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_creation_valide_derive_vendeur_et_conserve_ordre_images(
    client, vendeur, categorie, settings, tmp_path
):
    """Le vendeur JWT et les images reçues déterminent entièrement l'annonce créée."""
    settings.MEDIA_ROOT = tmp_path
    response = client.post(
        URL,
        donnees_annonce(
            categorie,
            images=[image_valide("un.png"), image_valide("deux.png")],
        ),
        **auth_headers(vendeur),
    )

    annonce = Annonce.objects.get()
    assert response.status_code == 201
    assert annonce.vendeur == vendeur
    assert annonce.statut == Annonce.Statut.EN_ATTENTE_MODERATION
    assert list(annonce.images.values_list("ordre", flat=True)) == [0, 1]
    assert len(response.json()["images"]) == 2


@pytest.mark.django_db
def test_creation_sans_image_est_refusee(client, vendeur, categorie):
    response = client.post(
        URL,
        donnees_annonce(categorie, images=[]),
        **auth_headers(vendeur),
    )

    assert response.status_code == 422
    assert Annonce.objects.count() == 0


@pytest.mark.django_db
def test_creation_avec_plus_de_huit_images_est_refusee(client, vendeur, categorie):
    response = client.post(
        URL,
        donnees_annonce(
            categorie,
            images=[image_valide(f"{index}.png") for index in range(9)],
        ),
        **auth_headers(vendeur),
    )

    assert response.status_code == 422
    assert Annonce.objects.count() == 0


@pytest.mark.django_db
def test_creation_prix_negatif_et_categorie_invalide_sont_refuses(client, vendeur, categorie):
    prix_negatif = client.post(
        URL,
        donnees_annonce(categorie, prix="-1.00"),
        **auth_headers(vendeur),
    )
    categorie_invalide = client.post(
        URL,
        donnees_annonce(categorie, categorie_id=999999),
        **auth_headers(vendeur),
    )

    assert prix_negatif.status_code == 422
    assert categorie_invalide.status_code == 422
    assert Annonce.objects.count() == 0


@pytest.mark.django_db
def test_creation_avec_coordonnees_construit_un_point_geographique(
    client, vendeur, categorie, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    response = client.post(
        URL,
        donnees_annonce(categorie, latitude="4.051056", longitude="9.767869"),
        **auth_headers(vendeur),
    )

    annonce = Annonce.objects.get()
    assert response.status_code == 201
    assert annonce.localisation is not None


@pytest.mark.django_db
def test_creation_sans_coordonnees_et_annonce_non_validee_invisible(
    client, vendeur, categorie, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    creation = client.post(URL, donnees_annonce(categorie), **auth_headers(vendeur))
    liste = client.get(URL)

    annonce = Annonce.objects.get()
    assert creation.status_code == 201
    assert annonce.localisation is None
    assert liste.status_code == 200
    assert liste.json() == []
