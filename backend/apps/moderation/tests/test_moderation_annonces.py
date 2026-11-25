"""Tests de la file et des décisions de modération des annonces."""
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Utilisateur
from apps.administration.models import JournalModeration
from apps.catalogue.models import Annonce, Categorie
from apps.catalogue.views import PREMIERE_PAGE_ANNONCES_CACHE_KEY


def auth_headers(utilisateur):
    """Construit une authentification JWT correspondant au rôle de test."""
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(utilisateur)}"}


@pytest.fixture
def categorie(db):
    """Crée la catégorie obligatoire de toute annonce à modérer."""
    return Categorie.objects.create(nom="Électronique", slug="electronique-moderation")


@pytest.fixture
def vendeur(db):
    """Crée le vendeur qui doit recevoir la décision de modération."""
    return Utilisateur.objects.create_user(
        nom="Vendeur", telephone="+237670000101", password="mot-de-passe-solide"
    )


@pytest.fixture
def moderateur(db):
    """Crée un compte ayant le rôle autorisé à modérer."""
    return Utilisateur.objects.create_user(
        nom="Modérateur",
        telephone="+237670000102",
        password="mot-de-passe-solide",
        role=Utilisateur.Role.MODERATEUR,
    )


def creer_annonce(vendeur, categorie, statut=Annonce.Statut.EN_ATTENTE_MODERATION):
    """Construit une annonce minimale dans l'état de modération demandé."""
    return Annonce.objects.create(
        vendeur=vendeur,
        categorie=categorie,
        titre="Téléphone à contrôler",
        description="Annonce en attente de validation.",
        prix="75000.00",
        ville="Douala",
        statut=statut,
    )


@pytest.mark.django_db
def test_file_moderation_est_triee_par_anciennete(client, vendeur, categorie, moderateur):
    """La première annonce créée apparaît en premier dans la file d'attente."""
    ancienne = creer_annonce(vendeur, categorie)
    recente = creer_annonce(vendeur, categorie)
    Annonce.objects.filter(pk=ancienne.pk).update(created_at=timezone.now() - timedelta(days=1))

    response = client.get("/v1/moderation/annonces", **auth_headers(moderateur))

    assert response.status_code == 200
    assert [annonce["id"] for annonce in response.json()] == [ancienne.id, recente.id]


@pytest.mark.django_db
def test_file_moderation_exclut_les_annonces_deja_traitees(
    client, vendeur, categorie, moderateur
):
    """La file ne contient strictement que les annonces en attente de décision."""
    attente = creer_annonce(vendeur, categorie)
    creer_annonce(vendeur, categorie, statut=Annonce.Statut.ACTIVE)
    creer_annonce(vendeur, categorie, statut=Annonce.Statut.REJETEE)

    response = client.get("/v1/moderation/annonces", **auth_headers(moderateur))

    assert response.status_code == 200
    assert [annonce["id"] for annonce in response.json()] == [attente.id]


@pytest.mark.django_db
def test_validation_active_annonce_journalise_et_notifie(
    client, vendeur, categorie, moderateur
):
    """Valider une annonce active sa visibilité et crée un audit immuable."""
    annonce = creer_annonce(vendeur, categorie)

    with patch("apps.moderation.views.NotificationService.notifier_decision_annonce") as notifier:
        response = client.post(
            f"/v1/moderation/annonces/{annonce.id}/decision",
            {"decision": "valider"},
            content_type="application/json",
            **auth_headers(moderateur),
        )

    annonce.refresh_from_db()
    journal = JournalModeration.objects.get(cible_id=annonce.id)
    assert response.status_code == 200
    assert annonce.statut == Annonce.Statut.ACTIVE
    assert annonce.date_publication is not None
    assert journal.moderateur == moderateur
    assert journal.action == "annonce_validee"
    assert journal.cible_type == "annonce"
    notifier.assert_called_once()


@pytest.mark.django_db
def test_rejet_exige_un_motif_et_le_conserve(client, vendeur, categorie, moderateur):
    """Un rejet non motivé est invalide, contrairement à un rejet documenté."""
    annonce = creer_annonce(vendeur, categorie)

    sans_motif = client.post(
        f"/v1/moderation/annonces/{annonce.id}/decision",
        {"decision": "rejeter"},
        content_type="application/json",
        **auth_headers(moderateur),
    )
    avec_motif = client.post(
        f"/v1/moderation/annonces/{annonce.id}/decision",
        {"decision": "rejeter", "motif": "Photos insuffisantes."},
        content_type="application/json",
        **auth_headers(moderateur),
    )

    annonce.refresh_from_db()
    assert sans_motif.status_code == 422
    assert avec_motif.status_code == 200
    assert annonce.statut == Annonce.Statut.REJETEE
    journal = JournalModeration.objects.get(cible_id=annonce.id)
    assert journal.details == "Photos insuffisantes."
    assert journal.action == "annonce_rejetee"
    assert journal.moderateur == moderateur


@pytest.mark.django_db
def test_annonce_deja_traitee_ne_peut_pas_recevoir_une_seconde_decision(
    client, vendeur, categorie, moderateur
):
    """La transition en attente vers un état final ne peut être appliquée qu'une fois."""
    annonce = creer_annonce(vendeur, categorie)

    premiere_decision = client.post(
        f"/v1/moderation/annonces/{annonce.id}/decision",
        {"decision": "valider"},
        content_type="application/json",
        **auth_headers(moderateur),
    )

    response = client.post(
        f"/v1/moderation/annonces/{annonce.id}/decision",
        {"decision": "rejeter", "motif": "Trop tard."},
        content_type="application/json",
        **auth_headers(moderateur),
    )

    assert premiere_decision.status_code == 200
    assert response.status_code == 409


@pytest.mark.django_db
def test_moderation_refuse_les_requetes_anonymes_et_donnees_invalides(
    client, vendeur, categorie, moderateur
):
    """Les routes protégées renvoient 401 sans JWT et 422 sur décision invalide."""
    annonce = creer_annonce(vendeur, categorie)

    file_anonyme = client.get("/v1/moderation/annonces")
    decision_anonyme = client.post(
        f"/v1/moderation/annonces/{annonce.id}/decision",
        {"decision": "valider"},
        content_type="application/json",
    )
    decision_invalide = client.post(
        f"/v1/moderation/annonces/{annonce.id}/decision",
        {"decision": "inconnue"},
        content_type="application/json",
        **auth_headers(moderateur),
    )

    assert file_anonyme.status_code == 401
    assert decision_anonyme.status_code == 401
    assert decision_invalide.status_code == 422


@pytest.mark.django_db
def test_decision_inexistante_renvoie_404(client, moderateur):
    """Une décision sur une annonce absente est normalisée sans erreur serveur."""
    response = client.post(
        "/v1/moderation/annonces/999999/decision",
        {"decision": "valider"},
        content_type="application/json",
        **auth_headers(moderateur),
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_validation_invalide_le_cache_et_notifie_aussi_un_rejet(
    client, vendeur, categorie, moderateur
):
    """Toute décision efface la liste publique et appelle le service vendeur."""
    annonce = creer_annonce(vendeur, categorie)
    cache.set(PREMIERE_PAGE_ANNONCES_CACHE_KEY, {"data": ["obsolete"]}, timeout=300)

    with patch("apps.moderation.views.NotificationService.notifier_decision_annonce") as notifier:
        response = client.post(
            f"/v1/moderation/annonces/{annonce.id}/decision",
            {"decision": "rejeter", "motif": "Non conforme."},
            content_type="application/json",
            **auth_headers(moderateur),
        )

    assert response.status_code == 200
    assert cache.get(PREMIERE_PAGE_ANNONCES_CACHE_KEY) is None
    notifier.assert_called_once()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "statut_attendu"),
    [
        (Utilisateur.Role.UTILISATEUR, 403),
        (Utilisateur.Role.LIVREUR, 403),
        (Utilisateur.Role.MODERATEUR, 200),
        (Utilisateur.Role.ADMINISTRATEUR, 200),
    ],
)
def test_permissions_de_moderation_suivent_le_role(
    client, vendeur, categorie, role, statut_attendu
):
    """Seuls modérateur et administrateur accèdent à la file de décision."""
    acteur = Utilisateur.objects.create_user(
        nom=f"Acteur {role}",
        telephone={
            Utilisateur.Role.UTILISATEUR: "+237670000111",
            Utilisateur.Role.LIVREUR: "+237670000112",
            Utilisateur.Role.MODERATEUR: "+237670000113",
            Utilisateur.Role.ADMINISTRATEUR: "+237670000114",
        }[role],
        password="mot-de-passe-solide",
        role=role,
    )
    annonce = creer_annonce(vendeur, categorie)

    file_attente = client.get("/v1/moderation/annonces", **auth_headers(acteur))
    decision = client.post(
        f"/v1/moderation/annonces/{annonce.id}/decision",
        {"decision": "valider"},
        content_type="application/json",
        **auth_headers(acteur),
    )

    assert file_attente.status_code == statut_attendu
    assert decision.status_code == statut_attendu
