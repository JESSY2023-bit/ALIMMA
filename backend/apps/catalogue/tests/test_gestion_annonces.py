"""Tests des actions qu'un vendeur peut réaliser sur ses propres annonces."""
from io import BytesIO
from os import urandom

import pytest
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, AnnonceImage, Categorie
from apps.catalogue.views import PREMIERE_PAGE_ANNONCES_CACHE_KEY


@pytest.fixture(autouse=True)
def vider_cache():
    """Isole les assertions de catalogue des réponses Redis mémorisées."""
    cache.clear()


def image_valide(nom="produit.png"):
    """Retourne une image réellement décodable pour les requêtes multipart."""
    contenu = BytesIO()
    Image.new("RGB", (2, 2), color="white").save(contenu, format="PNG")
    return SimpleUploadedFile(nom, contenu.getvalue(), content_type="image/png")


def image_trop_lourde(nom="trop-lourde.png"):
    """Produit une image PNG valide dont les octets dépassent réellement 5 Mo."""
    largeur, hauteur = 1600, 1200
    contenu = BytesIO()
    image = Image.frombytes("RGB", (largeur, hauteur), urandom(largeur * hauteur * 3))
    image.save(contenu, format="PNG")
    fichier = SimpleUploadedFile(nom, contenu.getvalue(), content_type="image/png")
    assert fichier.size > 5 * 1024 * 1024
    return fichier


def auth_headers(utilisateur):
    """Construit le header JWT du vendeur connecté."""
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(utilisateur)}"}


@pytest.fixture
def categorie(db):
    """Fournit une catégorie disponible pour les annonces de test."""
    return Categorie.objects.create(nom="Informatique", slug="informatique")


@pytest.fixture
def vendeur(db):
    """Crée le propriétaire de l'annonce testée."""
    return Utilisateur.objects.create_user(
        nom="Vendeur propriétaire",
        telephone="+237670000071",
        password="mot-de-passe-solide",
    )


def creer_annonce(vendeur, categorie, statut=Annonce.Statut.ACTIVE):
    """Crée une annonce persistée avec son image initiale."""
    annonce = Annonce.objects.create(
        vendeur=vendeur,
        categorie=categorie,
        titre="Ordinateur portable",
        description="Bon état, batterie récente.",
        prix="300000.00",
        ville="Douala",
        statut=statut,
    )
    AnnonceImage.objects.create(annonce=annonce, url="/media/annonces/test.png", ordre=0)
    return annonce


@pytest.mark.django_db
def test_proprietaire_modifie_annonce_et_retourne_en_moderation(client, vendeur, categorie):
    """Une modification substantielle d'annonce active exige une nouvelle validation."""
    annonce = creer_annonce(vendeur, categorie)

    response = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"titre": "Ordinateur portable reconditionné", "prix": "280000.00"},
        content_type="application/json",
        **auth_headers(vendeur),
    )

    annonce.refresh_from_db()
    assert response.status_code == 200
    assert annonce.titre == "Ordinateur portable reconditionné"
    assert annonce.statut == Annonce.Statut.EN_ATTENTE_MODERATION


@pytest.mark.django_db
def test_un_tiers_ne_peut_pas_modifier_annonce(client, vendeur, categorie):
    """Le contrôle objet renvoie 403 avant toute modification de l'annonce."""
    annonce = creer_annonce(vendeur, categorie)
    tiers = Utilisateur.objects.create_user(
        nom="Tiers", telephone="+237670000072", password="mot-de-passe-solide"
    )

    response = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"titre": "Tentative interdite"},
        content_type="application/json",
        **auth_headers(tiers),
    )

    annonce.refresh_from_db()
    assert response.status_code == 403
    assert annonce.titre == "Ordinateur portable"


@pytest.mark.django_db
def test_mutations_exigent_un_jwt(client, vendeur, categorie):
    """PATCH, DELETE et pause sont inaccessibles sans access token."""
    annonce = creer_annonce(vendeur, categorie)

    modification = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"titre": "Sans jeton"},
        content_type="application/json",
    )
    suppression = client.delete(f"/v1/annonces/{annonce.id}")
    pause = client.post(f"/v1/annonces/{annonce.id}/pause")

    assert modification.status_code == 401
    assert suppression.status_code == 401
    assert pause.status_code == 401


@pytest.mark.django_db
def test_suppression_est_logique(client, vendeur, categorie):
    """La suppression conserve l'enregistrement et le marque expiré."""
    annonce = creer_annonce(vendeur, categorie)

    response = client.delete(f"/v1/annonces/{annonce.id}", **auth_headers(vendeur))

    annonce.refresh_from_db()
    assert response.status_code == 204
    assert annonce.statut == Annonce.Statut.EXPIREE
    assert Annonce.objects.filter(pk=annonce.id).exists()


@pytest.mark.django_db
def test_un_tiers_ne_peut_ni_supprimer_ni_mettre_en_pause(client, vendeur, categorie):
    """Les deux mutations d'état appliquent la permission objet du vendeur."""
    annonce = creer_annonce(vendeur, categorie)
    tiers = Utilisateur.objects.create_user(
        nom="Tiers", telephone="+237670000073", password="mot-de-passe-solide"
    )

    suppression = client.delete(f"/v1/annonces/{annonce.id}", **auth_headers(tiers))
    pause = client.post(f"/v1/annonces/{annonce.id}/pause", **auth_headers(tiers))

    annonce.refresh_from_db()
    assert suppression.status_code == 403
    assert pause.status_code == 403
    assert annonce.statut == Annonce.Statut.ACTIVE


@pytest.mark.django_db
def test_pause_bascule_annonce_active_et_en_pause(client, vendeur, categorie):
    """La bascule retire puis remet l'annonce dans l'état public actif."""
    annonce = creer_annonce(vendeur, categorie)

    premiere_bascule = client.post(f"/v1/annonces/{annonce.id}/pause", **auth_headers(vendeur))
    liste_pendant_pause = client.get("/v1/annonces")
    annonce.refresh_from_db()
    seconde_bascule = client.post(f"/v1/annonces/{annonce.id}/pause", **auth_headers(vendeur))
    annonce.refresh_from_db()

    assert premiere_bascule.status_code == 200
    assert premiere_bascule.json()["statut"] == Annonce.Statut.EN_PAUSE
    assert liste_pendant_pause.json()["data"] == []
    assert seconde_bascule.status_code == 200
    assert annonce.statut == Annonce.Statut.ACTIVE


@pytest.mark.django_db
def test_annonce_vendue_ne_peut_plus_etre_modifiee(client, vendeur, categorie):
    """Les annonces vendues sont verrouillées pour préserver l'historique de vente."""
    annonce = creer_annonce(vendeur, categorie, statut=Annonce.Statut.VENDUE)

    response = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"prix": "1.00"},
        content_type="application/json",
        **auth_headers(vendeur),
    )

    assert response.status_code == 409


@pytest.mark.django_db
def test_annonce_vendue_ne_peut_ni_etre_supprimee_ni_mise_en_pause(
    client, vendeur, categorie
):
    """Aucune transition ne doit modifier une annonce déjà vendue."""
    annonce = creer_annonce(vendeur, categorie, statut=Annonce.Statut.VENDUE)

    suppression = client.delete(f"/v1/annonces/{annonce.id}", **auth_headers(vendeur))
    pause = client.post(f"/v1/annonces/{annonce.id}/pause", **auth_headers(vendeur))

    assert suppression.status_code == 409
    assert pause.status_code == 409


@pytest.mark.django_db
def test_patch_refuse_les_valeurs_et_images_invalides(client, vendeur, categorie):
    """Les validations de création restent appliquées lors de la modification."""
    annonce = creer_annonce(vendeur, categorie)
    categorie_invalide = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"categorie_id": 999999},
        content_type="application/json",
        **auth_headers(vendeur),
    )
    prix_negatif = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"prix": "-1"},
        content_type="application/json",
        **auth_headers(vendeur),
    )
    coordonnees_incompletes = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"latitude": "4.0"},
        content_type="application/json",
        **auth_headers(vendeur),
    )
    derniere_image = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"images_supprimees": [annonce.images.get().id]},
        content_type="application/json",
        **auth_headers(vendeur),
    )

    assert categorie_invalide.status_code == 422
    assert prix_negatif.status_code == 422
    assert coordonnees_incompletes.status_code == 422
    assert derniere_image.status_code == 422


@pytest.mark.django_db
def test_patch_refuse_les_images_falsifiees_ou_en_nombre_excessif(
    vendeur, categorie, settings, tmp_path
):
    """Le contenu réel et le plafond de huit images sont vérifiés en modification."""
    settings.MEDIA_ROOT = tmp_path
    annonce = creer_annonce(vendeur, categorie)
    api_client = APIClient()
    api_client.credentials(**auth_headers(vendeur))
    faux_fichier = SimpleUploadedFile(
        "faux.png",
        b"ceci-n-est-pas-une-image",
        content_type="image/png",
    )
    fichier_trop_lourd = image_trop_lourde()

    falsifiee = api_client.patch(
        f"/v1/annonces/{annonce.id}",
        {"images_ajoutees": [faux_fichier]},
        format="multipart",
    )
    trop_lourde = api_client.patch(
        f"/v1/annonces/{annonce.id}",
        {"images_ajoutees": [fichier_trop_lourd]},
        format="multipart",
    )
    excessives = api_client.patch(
        f"/v1/annonces/{annonce.id}",
        {"images_ajoutees": [image_valide(f"{index}.png") for index in range(8)]},
        format="multipart",
    )

    assert falsifiee.status_code == 422
    assert trop_lourde.status_code == 422
    assert excessives.status_code == 422


@pytest.mark.django_db
def test_modification_des_images_conserve_leur_ordre_et_repasse_en_moderation(
    vendeur, categorie, settings, tmp_path
):
    """Un ajout et une suppression d'image sont atomiques du point de vue métier."""
    settings.MEDIA_ROOT = tmp_path
    annonce = creer_annonce(vendeur, categorie)
    image_initiale = annonce.images.get()
    api_client = APIClient()
    api_client.credentials(**auth_headers(vendeur))

    response = api_client.patch(
        f"/v1/annonces/{annonce.id}",
        {
            "images_ajoutees": [image_valide("nouvelle.png")],
            "images_supprimees": [image_initiale.id],
        },
        format="multipart",
    )

    annonce.refresh_from_db()
    assert response.status_code == 200
    assert annonce.statut == Annonce.Statut.EN_ATTENTE_MODERATION
    assert annonce.images.count() == 1
    assert annonce.images.get().ordre == 0


@pytest.mark.django_db
def test_mes_annonces_expose_le_nombre_de_vues(client, vendeur, categorie):
    """Le vendeur voit toutes ses annonces avec nb_vues, même non actives."""
    annonce = creer_annonce(vendeur, categorie, statut=Annonce.Statut.EN_PAUSE)
    annonce.nb_vues = 12
    annonce.save(update_fields=["nb_vues"])

    response = client.get("/v1/utilisateurs/moi/annonces", **auth_headers(vendeur))

    assert response.status_code == 200
    assert response.json()[0]["id"] == annonce.id
    assert response.json()[0]["nb_vues"] == 12


@pytest.mark.django_db
def test_mes_annonces_n_expose_que_celles_du_compte_connecte(client, vendeur, categorie):
    """Le vendeur connecté ne reçoit jamais les annonces d'un autre compte."""
    creer_annonce(vendeur, categorie)
    autre = Utilisateur.objects.create_user(
        nom="Autre", telephone="+237670000074", password="mot-de-passe-solide"
    )
    creer_annonce(autre, categorie)

    response = client.get("/v1/utilisateurs/moi/annonces", **auth_headers(vendeur))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["vendeur_id"] == vendeur.id


@pytest.mark.django_db
def test_mes_annonces_exige_un_jwt(client):
    """La liste privée du vendeur ne doit pas être accessible anonymement."""
    assert client.get("/v1/utilisateurs/moi/annonces").status_code == 401


@pytest.mark.django_db
def test_detail_public_actif_incremente_les_vues_et_masque_les_autres_etats(
    client, vendeur, categorie
):
    """Le détail public suit le même filtre d'activité que la liste publique."""
    active = creer_annonce(vendeur, categorie)
    pausee = creer_annonce(vendeur, categorie, statut=Annonce.Statut.EN_PAUSE)

    detail = client.get(f"/v1/annonces/{active.id}")
    non_public = client.get(f"/v1/annonces/{pausee.id}")

    active.refresh_from_db()
    assert detail.status_code == 200
    assert detail.json()["id"] == active.id
    assert active.nb_vues == 1
    assert non_public.status_code == 404


@pytest.mark.django_db
def test_pause_invalide_la_premiere_page_publique_en_cache(client, vendeur, categorie):
    """Une annonce mise en pause ne peut pas rester visible dans la réponse mémorisée."""
    annonce = creer_annonce(vendeur, categorie)
    cache.set(PREMIERE_PAGE_ANNONCES_CACHE_KEY, {"data": ["obsolete"]}, timeout=300)

    response = client.post(f"/v1/annonces/{annonce.id}/pause", **auth_headers(vendeur))

    assert response.status_code == 200
    assert cache.get(PREMIERE_PAGE_ANNONCES_CACHE_KEY) is None


@pytest.mark.django_db
def test_modification_et_suppression_invalident_le_cache(client, vendeur, categorie):
    """Aucune mutation d'annonce ne doit laisser la première page obsolète."""
    annonce = creer_annonce(vendeur, categorie)
    cache.set(PREMIERE_PAGE_ANNONCES_CACHE_KEY, {"data": ["obsolete"]}, timeout=300)

    modification = client.patch(
        f"/v1/annonces/{annonce.id}",
        {"titre": "Titre modifié"},
        content_type="application/json",
        **auth_headers(vendeur),
    )
    assert modification.status_code == 200
    assert cache.get(PREMIERE_PAGE_ANNONCES_CACHE_KEY) is None

    cache.set(PREMIERE_PAGE_ANNONCES_CACHE_KEY, {"data": ["obsolete"]}, timeout=300)
    suppression = client.delete(f"/v1/annonces/{annonce.id}", **auth_headers(vendeur))
    assert suppression.status_code == 204
    assert cache.get(PREMIERE_PAGE_ANNONCES_CACHE_KEY) is None
