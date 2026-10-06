"""Tests du profil personnel, public et du changement de mot de passe."""
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient
import pytest

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, Categorie

MON_PROFIL_URL = "/v1/utilisateurs/moi"
MOT_DE_PASSE_URL = "/v1/utilisateurs/moi/mot-de-passe"


def png_valide():
    """Produit des octets PNG valides pour tester la vérification Pillow réelle."""
    output = BytesIO()
    Image.new("RGB", (1, 1), color="white").save(output, format="PNG")
    return output.getvalue()


@pytest.fixture
def utilisateur(db):
    """Crée le titulaire du JWT utilisé dans les scénarios de profil."""
    return Utilisateur.objects.create_user(
        nom="Alice Ngono",
        email="alice@example.cm",
        telephone="+237670000001",
        password="mot-de-passe-solide",
    )


def auth_headers(utilisateur):
    """Construit l'en-tête Bearer reconnu par l'authentification JWT DRF."""
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(utilisateur)}"}


def creer_annonce(utilisateur):
    """Crée l'activité de vente minimale requise pour rendre un profil public."""
    categorie, _ = Categorie.objects.get_or_create(
        slug="telephones",
        defaults={"nom": "Téléphones"},
    )
    return Annonce.objects.create(
        vendeur=utilisateur,
        categorie=categorie,
        titre="Téléphone de test",
        description="Annonce créée exclusivement pour vérifier le profil public.",
        prix=Decimal("10000.00"),
        ville="Douala",
    )


@pytest.mark.django_db
def test_lecture_du_profil_personnel(client, utilisateur):
    """Le titulaire d'un JWT lit ses données complètes sans son hash de mot de passe."""
    response = client.get(MON_PROFIL_URL, **auth_headers(utilisateur))

    assert response.status_code == 200
    assert response.json()["email"] == utilisateur.email
    assert "password_hash" not in response.json()


@pytest.mark.django_db
def test_profil_personnel_refuse_sans_authentification(client):
    """Les routes ``moi`` nécessitent explicitement un access token valide."""
    response = client.get(MON_PROFIL_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_mise_a_jour_partielle_du_profil(client, utilisateur):
    """Une modification ne touche que les champs autorisés reçus dans le PATCH."""
    response = client.patch(
        MON_PROFIL_URL,
        {"nom": "Alice Modifiée", "photo_url": "https://images.example/alice.jpg"},
        content_type="application/json",
        **auth_headers(utilisateur),
    )

    utilisateur.refresh_from_db()
    assert response.status_code == 200
    assert utilisateur.nom == "Alice Modifiée"
    assert utilisateur.photo_url == "https://images.example/alice.jpg"


@pytest.mark.django_db
def test_mise_a_jour_refuse_un_email_utilise_par_un_autre_compte(client, utilisateur):
    """L'unicité de l'e-mail est maintenue lors de la mise à jour du profil."""
    Utilisateur.objects.create_user(
        nom="Paul Ndzi",
        email="paul@example.cm",
        telephone="+237670000002",
        password="mot-de-passe-solide",
    )

    response = client.patch(
        MON_PROFIL_URL,
        {"email": "paul@example.cm"},
        content_type="application/json",
        **auth_headers(utilisateur),
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.django_db
def test_mise_a_jour_du_profil_refuse_sans_jwt(client):
    """Le PATCH du profil personnel exige un access token."""
    response = client.patch(
        MON_PROFIL_URL,
        {"nom": "Alice Modifiée"},
        content_type="application/json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_upload_photo_de_profil_valide(utilisateur, settings, tmp_path):
    """Une image autorisée est enregistrée par le stockage Django configuré."""
    settings.MEDIA_ROOT = tmp_path
    photo = SimpleUploadedFile("avatar.png", png_valide(), content_type="image/png")

    api_client = APIClient()
    api_client.credentials(**auth_headers(utilisateur))
    response = api_client.patch(
        MON_PROFIL_URL,
        {"photo": photo},
        # DRF encode correctement le corps multipart d'une requête PATCH, tel
        # qu'il sera envoyé par ``FormData`` côté frontend.
        format="multipart",
    )

    utilisateur.refresh_from_db()
    assert response.status_code == 200
    assert utilisateur.photo_url.startswith("/media/profils/")
    assert (tmp_path / utilisateur.photo_url.removeprefix("/media/")).is_file()


@pytest.mark.django_db
def test_upload_photo_refuse_un_fichier_superieur_a_deux_mo(utilisateur):
    """La limite de taille est appliquée avant tout enregistrement du fichier."""
    photo = SimpleUploadedFile(
        "trop-grand.png",
        b"x" * (2 * 1024 * 1024 + 1),
        content_type="image/png",
    )
    api_client = APIClient()
    api_client.credentials(**auth_headers(utilisateur))

    response = api_client.patch(MON_PROFIL_URL, {"photo": photo}, format="multipart")

    assert response.status_code == 422


@pytest.mark.django_db
def test_upload_photo_refuse_un_mime_falsifie(utilisateur):
    """Un MIME image déclaré ne contourne pas la vérification Pillow du contenu."""
    photo = SimpleUploadedFile("faux.png", b"ceci-n-est-pas-une-image", content_type="image/png")
    api_client = APIClient()
    api_client.credentials(**auth_headers(utilisateur))

    response = api_client.patch(MON_PROFIL_URL, {"photo": photo}, format="multipart")

    assert response.status_code == 422


@pytest.mark.django_db
def test_upload_photo_refuse_un_mime_interdit(utilisateur):
    """Le MIME déclaré doit appartenir aux types autorisés, même si le contenu est une image."""
    photo = SimpleUploadedFile("avatar.pdf", png_valide(), content_type="application/pdf")
    api_client = APIClient()
    api_client.credentials(**auth_headers(utilisateur))

    response = api_client.patch(MON_PROFIL_URL, {"photo": photo}, format="multipart")

    assert response.status_code == 422


@pytest.mark.django_db
def test_changement_de_mot_de_passe_valide(client, utilisateur):
    """Un ancien secret correct est remplacé par un hash bcrypt du nouveau."""
    response = client.put(
        MOT_DE_PASSE_URL,
        {
            "ancien_mot_de_passe": "mot-de-passe-solide",
            "nouveau_mot_de_passe": "nouveau-mot-de-passe",
        },
        content_type="application/json",
        **auth_headers(utilisateur),
    )

    utilisateur.refresh_from_db()
    assert response.status_code == 204
    assert utilisateur.check_password("nouveau-mot-de-passe")
    assert not utilisateur.check_password("mot-de-passe-solide")


@pytest.mark.django_db
def test_changement_de_mot_de_passe_refuse_un_ancien_secret_incorrect(client, utilisateur):
    """Un ancien mot de passe erroné produit l'erreur standard 401."""
    response = client.put(
        MOT_DE_PASSE_URL,
        {
            "ancien_mot_de_passe": "secret-invalide",
            "nouveau_mot_de_passe": "nouveau-mot-de-passe",
        },
        content_type="application/json",
        **auth_headers(utilisateur),
    )

    assert response.status_code == 401
    assert set(response.json()) == {"code", "message"}


@pytest.mark.django_db
def test_changement_de_mot_de_passe_refuse_sans_jwt(client):
    """Le changement de mot de passe reste inaccessible sans access token."""
    response = client.put(
        MOT_DE_PASSE_URL,
        {
            "ancien_mot_de_passe": "mot-de-passe-solide",
            "nouveau_mot_de_passe": "nouveau-mot-de-passe",
        },
        content_type="application/json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_changement_de_mot_de_passe_refuse_un_nouveau_secret_trop_court(client, utilisateur):
    """Le nouveau mot de passe respecte le minimum de huit caractères."""
    response = client.put(
        MOT_DE_PASSE_URL,
        {
            "ancien_mot_de_passe": "mot-de-passe-solide",
            "nouveau_mot_de_passe": "court",
        },
        content_type="application/json",
        **auth_headers(utilisateur),
    )

    assert response.status_code == 422


@pytest.mark.django_db
def test_profil_public_ne_fuit_aucune_donnee_personnelle(client, utilisateur):
    """Toute personne peut lire le profil public sans e-mail, téléphone ni rôle."""
    creer_annonce(utilisateur)
    response = client.get(f"/v1/utilisateurs/{utilisateur.id}")

    assert response.status_code == 200
    assert set(response.json()) == {
        "id",
        "nom",
        "photo_url",
        "note_moyenne",
        "nb_avis",
        "date_inscription",
    }


@pytest.mark.django_db
def test_profil_public_inexistant_renvoie_404(client):
    """Un identifiant inconnu ne révèle aucune donnée et retourne une 404 standard."""
    response = client.get("/v1/utilisateurs/999999")

    assert response.status_code == 404


@pytest.mark.django_db
def test_profil_public_refuse_un_compte_standard_sans_annonce(client, utilisateur):
    """Un compte standard sans activité de vente est indiscernable d'un identifiant absent."""
    response = client.get(f"/v1/utilisateurs/{utilisateur.id}")

    assert response.status_code == 404


@pytest.mark.django_db
def test_profil_public_accepte_un_compte_standard_avec_annonce(client, utilisateur):
    """Un compte utilisateur devient visible dès qu'il possède une annonce."""
    creer_annonce(utilisateur)

    response = client.get(f"/v1/utilisateurs/{utilisateur.id}")

    assert response.status_code == 200


@pytest.mark.django_db
def test_profil_public_accepte_un_vendeur_pro_avec_annonce(client, utilisateur):
    """Le rôle vendeur_pro reste visible lorsqu'une annonce existe."""
    utilisateur.role = Utilisateur.Role.VENDEUR_PRO
    utilisateur.save(update_fields=["role", "updated_at"])
    creer_annonce(utilisateur)

    response = client.get(f"/v1/utilisateurs/{utilisateur.id}")

    assert response.status_code == 200


@pytest.mark.django_db
def test_profil_public_refuse_un_vendeur_pro_sans_annonce(client, utilisateur):
    """Le rôle vendeur_pro seul ne rend pas un profil public."""
    utilisateur.role = Utilisateur.Role.VENDEUR_PRO
    utilisateur.save(update_fields=["role", "updated_at"])

    response = client.get(f"/v1/utilisateurs/{utilisateur.id}")

    assert response.status_code == 404


@pytest.mark.django_db
def test_mise_a_jour_ignore_les_champs_privilegies(client, utilisateur):
    """La liste blanche du sérialiseur bloque toute élévation de privilèges par PATCH."""
    response = client.patch(
        MON_PROFIL_URL,
        {
            "role": Utilisateur.Role.ADMINISTRATEUR,
            "telephone": "+237699999999",
            "est_actif": False,
        },
        content_type="application/json",
        **auth_headers(utilisateur),
    )

    utilisateur.refresh_from_db()
    assert response.status_code == 200
    assert utilisateur.role == Utilisateur.Role.UTILISATEUR
    assert utilisateur.telephone == "+237670000001"
    assert utilisateur.est_actif is True
