"""Tests du stockage configurable et de la migration des médias historiques."""
from io import BytesIO

import pytest
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from PIL import Image
from apps.accounts.models import Utilisateur
from apps.accounts.serializers import ProfilUpdateSerializer
from apps.catalogue.models import Annonce, AnnonceImage, Categorie
from apps.catalogue.serializers import AnnonceCreationSerializer


STORAGES_MEMOIRE = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


def image_test(nom="image.png"):
    """Construit une image PNG compacte réellement lisible par Pillow."""
    contenu = BytesIO()
    Image.new("RGB", (8, 8), color="red").save(contenu, format="PNG")
    return SimpleUploadedFile(nom, contenu.getvalue(), content_type="image/png")


@pytest.mark.django_db
@override_settings(STORAGES=STORAGES_MEMOIRE, MEDIA_URL="https://media.test/")
def test_uploads_utilisent_le_stockage_configure_et_des_noms_webp_opacifies():
    """Les photos et annonces utilisent le backend mémoire et des UUID WebP."""
    utilisateur = Utilisateur.objects.create_user(
        nom="Média", telephone="+237670001111", password="mot-de-passe-solide"
    )
    categorie = Categorie.objects.create(nom="Médias", slug="medias")

    profil = ProfilUpdateSerializer(
        utilisateur,
        data={"photo": image_test("avatar.png")},
        partial=True,
    )
    assert profil.is_valid(), profil.errors
    utilisateur = profil.save()

    annonce_serializer = AnnonceCreationSerializer(
        data={
            "titre": "Téléphone", "description": "Image stockée.", "prix": "1000",
            "categorie_id": categorie.id, "ville": "Douala", "etat": "occasion",
            "type_vente": "fixe", "images": [image_test("produit.png")],
        },
        context={"vendeur": utilisateur},
    )
    assert annonce_serializer.is_valid(), annonce_serializer.errors
    annonce = annonce_serializer.save()
    image_annonce = annonce.images.get()

    for url, prefixe in (
        (utilisateur.photo_url, f"profils/{utilisateur.id}/"),
        (image_annonce.url, f"annonces/{annonce.id}/"),
    ):
        assert url.startswith("https://media.test/" + prefixe)
        assert url.endswith(".webp")
        assert default_storage.exists(url.removeprefix("https://media.test/"))


@pytest.mark.django_db
@override_settings(STORAGES=STORAGES_MEMOIRE, MEDIA_URL="https://media.test/")
def test_migrer_medias_est_idempotente_et_sait_simuler(tmp_path):
    """La commande copie les URL locales une fois sans modifier le stockage au dry-run."""
    utilisateur = Utilisateur.objects.create_user(
        nom="Ancien média", telephone="+237670001112", password="mot-de-passe-solide",
        photo_url="/media/profils/ancien.png",
    )
    categorie = Categorie.objects.create(nom="Anciens", slug="anciens")
    annonce = Annonce.objects.create(
        vendeur=utilisateur, categorie=categorie, titre="Ancien", description="Ancienne image",
        prix="1000", ville="Douala",
    )
    image_annonce = AnnonceImage.objects.create(
        annonce=annonce, url="/media/annonces/ancien.png", ordre=0
    )
    for nom in ("profils/ancien.png", "annonces/ancien.png"):
        cible = tmp_path / nom
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_bytes(image_test().read())

    call_command("migrer_medias", "--source-root", str(tmp_path), "--dry-run")
    utilisateur.refresh_from_db()
    image_annonce.refresh_from_db()
    assert utilisateur.photo_url == "/media/profils/ancien.png"
    assert image_annonce.url == "/media/annonces/ancien.png"

    call_command("migrer_medias", "--source-root", str(tmp_path))
    utilisateur.refresh_from_db()
    image_annonce.refresh_from_db()
    urls_apres_migration = (utilisateur.photo_url, image_annonce.url)
    assert all(url.startswith("https://media.test/") for url in urls_apres_migration)

    call_command("migrer_medias", "--source-root", str(tmp_path))
    utilisateur.refresh_from_db()
    image_annonce.refresh_from_db()
    assert (utilisateur.photo_url, image_annonce.url) == urls_apres_migration
