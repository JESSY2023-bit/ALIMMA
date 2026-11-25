"""Tests de la commande sûre de création du premier administrateur."""
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.accounts.models import Utilisateur
from apps.administration.models import JournalModeration


TELEPHONE = "+237677451289"
MOT_DE_PASSE = "Orage!Baobab2026"


def executer_commande(monkeypatch, **options):
    """Lance la commande avec un secret temporaire absent des arguments CLI."""
    monkeypatch.setenv("ALIMMA_ADMIN_PASSWORD", MOT_DE_PASSE)
    sortie = StringIO()
    erreur = StringIO()
    call_command("creer_administrateur", stdout=sortie, stderr=erreur, **options)
    return sortie.getvalue(), erreur.getvalue()


@pytest.mark.django_db
def test_creation_admin_normalise_le_telephone_et_permet_la_connexion(client, monkeypatch):
    """Le premier admin peut immédiatement obtenir un JWT avec son E.164 normalisé."""
    sortie, _ = executer_commande(
        monkeypatch,
        telephone="677451289",
        nom="Administrateur Test",
        email="ADMIN@EXAMPLE.TEST",
    )

    administrateur = Utilisateur.objects.get(telephone=TELEPHONE)
    connexion = client.post(
        "/v1/auth/login",
        {"identifiant": TELEPHONE, "password": MOT_DE_PASSE},
        content_type="application/json",
    )

    assert administrateur.role == Utilisateur.Role.ADMINISTRATEUR
    assert administrateur.is_superuser is True
    assert administrateur.is_staff is True
    assert administrateur.email == "admin@example.test"
    assert connexion.status_code == 200
    assert MOT_DE_PASSE not in sortie
    assert administrateur.password_hash not in sortie


@pytest.mark.django_db
def test_telephone_invalide_est_refuse(monkeypatch):
    """La commande utilise exactement la politique E.164 camerounaise de l'API."""
    with pytest.raises(CommandError, match=r"format \+237"):
        executer_commande(monkeypatch, telephone="123", nom="Admin Test")


@pytest.mark.django_db
def test_mot_de_passe_trop_court_est_refuse(monkeypatch):
    """Un administrateur impose un minimum supérieur à celui d'une inscription."""
    monkeypatch.setenv("ALIMMA_ADMIN_PASSWORD", "Court!2026")

    with pytest.raises(CommandError, match="au moins 12"):
        call_command("creer_administrateur", telephone=TELEPHONE, nom="Admin Test")

    assert not Utilisateur.objects.exists()


@pytest.mark.django_db
def test_confirmations_getpass_differentes_sont_refusees(monkeypatch):
    """L'entrée interactive exige deux valeurs strictement identiques."""
    monkeypatch.delenv("ALIMMA_ADMIN_PASSWORD", raising=False)
    saisies = iter([MOT_DE_PASSE, "Different!2026"])
    monkeypatch.setattr(
        "apps.accounts.management.commands.creer_administrateur.getpass.getpass",
        lambda _: next(saisies),
    )

    with pytest.raises(CommandError, match="ne correspondent pas"):
        call_command("creer_administrateur", telephone=TELEPHONE, nom="Admin Test")

    assert not Utilisateur.objects.exists()


@pytest.mark.django_db
def test_relance_admin_existante_ne_modifie_rien(monkeypatch):
    """Une relance sans option reste idempotente et ne crée aucun journal supplémentaire."""
    executer_commande(monkeypatch, telephone=TELEPHONE, nom="Admin Test")
    administrateur = Utilisateur.objects.get(telephone=TELEPHONE)
    mot_de_passe = administrateur.password_hash
    journal_count = JournalModeration.objects.count()

    sortie, _ = executer_commande(monkeypatch, telephone=TELEPHONE)
    administrateur.refresh_from_db()

    assert "déjà administrateur" in sortie
    assert administrateur.password_hash == mot_de_passe
    assert JournalModeration.objects.count() == journal_count


@pytest.mark.django_db
def test_promotion_conserve_le_mot_de_passe_et_journalise(monkeypatch):
    """Un compte existant exige une confirmation explicite avant sa promotion."""
    utilisateur = Utilisateur.objects.create_user(
        nom="Compte Test",
        telephone=TELEPHONE,
        password=MOT_DE_PASSE,
    )
    mot_de_passe = utilisateur.password_hash

    with pytest.raises(CommandError, match="--promouvoir"):
        executer_commande(monkeypatch, telephone=TELEPHONE)

    executer_commande(monkeypatch, telephone=TELEPHONE, promouvoir=True)
    utilisateur.refresh_from_db()

    assert utilisateur.role == Utilisateur.Role.ADMINISTRATEUR
    assert utilisateur.est_actif is True
    assert utilisateur.password_hash == mot_de_passe
    assert JournalModeration.objects.filter(
        moderateur=utilisateur,
        action="promotion_administrateur",
        cible_type="utilisateur",
        cible_id=utilisateur.id,
    ).exists()


@pytest.mark.django_db
def test_reinitialisation_mot_de_passe_journalise(monkeypatch):
    """La réinitialisation explicite remplace le hash et laisse une trace métier."""
    executer_commande(monkeypatch, telephone=TELEPHONE, nom="Admin Test")
    administrateur = Utilisateur.objects.get(telephone=TELEPHONE)
    ancien_hash = administrateur.password_hash
    nouveau_mot_de_passe = "Vent!Mangue2026"
    monkeypatch.setenv("ALIMMA_ADMIN_PASSWORD", nouveau_mot_de_passe)

    sortie = StringIO()
    call_command(
        "creer_administrateur",
        telephone=TELEPHONE,
        reinitialiser_mot_de_passe=True,
        stdout=sortie,
    )
    administrateur.refresh_from_db()

    assert administrateur.password_hash != ancien_hash
    assert administrateur.check_password(nouveau_mot_de_passe)
    assert JournalModeration.objects.filter(
        action="reinitialisation_mdp_administrateur",
        cible_id=administrateur.id,
    ).exists()
    assert nouveau_mot_de_passe not in sortie.getvalue()


@pytest.mark.django_db
def test_dry_run_ne_cree_ni_ne_modifie(monkeypatch):
    """Une simulation sert à vérifier la cible Neon sans écrire dans sa base."""
    sortie, _ = executer_commande(
        monkeypatch,
        telephone=TELEPHONE,
        nom="Admin Test",
        dry_run=True,
    )

    assert "Simulation" in sortie
    assert not Utilisateur.objects.exists()
    assert not JournalModeration.objects.exists()


@pytest.mark.django_db
def test_email_deja_utilise_est_refuse(monkeypatch):
    """La commande préserve l'unicité de l'e-mail des comptes ALIMMA."""
    Utilisateur.objects.create_user(
        nom="Autre Compte",
        telephone="+237699000001",
        email="deja@example.test",
        password=MOT_DE_PASSE,
    )

    with pytest.raises(CommandError, match="déjà utilisée"):
        executer_commande(
            monkeypatch,
            telephone=TELEPHONE,
            nom="Admin Test",
            email="DEJA@example.test",
        )

    assert Utilisateur.objects.filter(telephone=TELEPHONE).count() == 0


@pytest.mark.django_db
def test_journal_creation_ne_contient_aucun_secret(monkeypatch):
    """Les sorties et détails d'audit ne doivent jamais divulguer le mot de passe."""
    sortie, erreur = executer_commande(monkeypatch, telephone=TELEPHONE, nom="Admin Test")
    journal = JournalModeration.objects.get(action="creation_administrateur")

    assert MOT_DE_PASSE not in sortie + erreur + (journal.details or "")
