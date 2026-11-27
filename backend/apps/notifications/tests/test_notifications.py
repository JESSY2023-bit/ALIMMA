"""Tests des gabarits et de l'envoi idempotent par le worker RQ."""
import logging

import pytest

from apps.accounts.models import Utilisateur
from apps.notifications.models import Notification
from apps.notifications.services import notifier
from apps.notifications.tasks import envoyer_notification
from apps.notifications.templates import rendre_gabarit


@pytest.fixture
def utilisateur(db):
    """Crée un destinataire de test avec une adresse et un téléphone valides."""
    return Utilisateur.objects.create_user(
        nom="Alice Notification",
        email="alice.notifications@example.com",
        telephone="+237670008001",
        password="mot-de-passe-solide",
    )


def test_gabarits_francais_et_anglais_sont_courts():
    """Les deux langues restent adaptées à la limite d'un SMS transactionnel."""
    contexte = {"titre": "Téléphone", "motif": "Photos insuffisantes"}

    francais = rendre_gabarit("annonce_rejetee", contexte, "fr")
    anglais = rendre_gabarit("annonce_rejetee", contexte, "en")

    assert "rejetée" in francais
    assert "rejected" in anglais
    assert len(francais) <= 160
    assert len(anglais) <= 160


@pytest.mark.django_db
def test_sms_console_est_envoye_et_le_cout_est_trace(utilisateur, settings):
    """Le transport local passe la notification à envoyée sans coût facturé."""
    settings.SMS_PROVIDER = "console"
    notification = Notification.objects.create(
        destinataire=utilisateur,
        canal=Notification.Canal.SMS,
        gabarit="annonce_validee",
        contexte={"titre": "Téléphone"},
        cout_fcfa=25,
    )

    envoyer_notification(notification.id)

    notification.refresh_from_db()
    assert notification.statut == Notification.Statut.ENVOYEE
    assert notification.tentatives == 1
    assert notification.fournisseur == "console"
    assert notification.cout_fcfa == 0
    assert notification.envoyee_at is not None


@pytest.mark.django_db(transaction=True)
def test_notifier_utilise_rq_en_mode_synchrone(utilisateur, settings):
    """La file exécute immédiatement le travail lorsque RQ_ASYNC est désactivé."""
    settings.RQ_ASYNC = False
    settings.SMS_PROVIDER = "console"

    notifications = notifier(
        utilisateur,
        "annonce_validee",
        {"titre": "Téléphone"},
        canaux=(Notification.Canal.SMS,),
    )

    notification = notifications[0]
    notification.refresh_from_db()
    assert notification.statut == Notification.Statut.ENVOYEE


@pytest.mark.django_db
def test_echec_fournisseur_est_reessaye_puis_termine_en_echec(
    utilisateur, monkeypatch, caplog
):
    """Trois échecs aboutissent à un état final sans log de numéro ni de clé."""
    notification = Notification.objects.create(
        destinataire=utilisateur,
        canal=Notification.Canal.SMS,
        gabarit="annonce_validee",
        contexte={"titre": "Téléphone"},
    )

    class FournisseurEnEchec:
        """Double de test ne divulguant pas le contenu de l'appel."""

        nom = "test"

        def envoyer(self, telephone, message):
            raise RuntimeError("indisponible")

    monkeypatch.setattr(
        "apps.notifications.tasks.fournisseur_sms", lambda: FournisseurEnEchec()
    )
    with caplog.at_level(logging.WARNING):
        for tentative in range(3):
            if tentative < 2:
                with pytest.raises(RuntimeError, match="indisponible"):
                    envoyer_notification(notification.id)
            else:
                envoyer_notification(notification.id)

    notification.refresh_from_db()
    assert notification.tentatives == 3
    assert notification.statut == Notification.Statut.ECHEC
    assert utilisateur.telephone not in caplog.text
    assert "SMS_API_KEY" not in caplog.text


@pytest.mark.django_db
def test_notification_deja_envoyee_est_idempotente(utilisateur):
    """Une relance ne réexpédie pas une notification déjà acquittée."""
    notification = Notification.objects.create(
        destinataire=utilisateur,
        canal=Notification.Canal.SMS,
        gabarit="annonce_validee",
        contexte={"titre": "Téléphone"},
        statut=Notification.Statut.ENVOYEE,
        tentatives=1,
    )

    envoyer_notification(notification.id)

    notification.refresh_from_db()
    assert notification.tentatives == 1
