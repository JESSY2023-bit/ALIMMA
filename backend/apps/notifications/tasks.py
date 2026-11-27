"""Tâches RQ idempotentes responsables de l'envoi effectif."""
import logging

from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import Notification
from .providers import fournisseur_sms
from .templates import rendre_gabarit

logger = logging.getLogger(__name__)
MAX_TENTATIVES = 3


def envoyer_notification(notification_id):
    """Envoie une notification en attente, sans renvoyer une notification déjà réussie."""
    with transaction.atomic():
        notification = (
            Notification.objects.select_for_update()
            .select_related("destinataire")
            .get(pk=notification_id)
        )
        if notification.statut == Notification.Statut.ENVOYEE:
            return
        if notification.tentatives >= MAX_TENTATIVES:
            notification.statut = Notification.Statut.ECHEC
            notification.save(update_fields=["statut"])
            return
        notification.tentatives += 1
        notification.save(update_fields=["tentatives"])

    try:
        langue = notification.destinataire.langue
        message = rendre_gabarit(notification.gabarit, notification.contexte, langue)
        if notification.canal == Notification.Canal.SMS:
            fournisseur = fournisseur_sms()
            fournisseur.envoyer(notification.destinataire.telephone, message)
            fournisseur_nom = fournisseur.nom
            cout = 0 if fournisseur_nom == "console" else notification.cout_fcfa
        else:
            if notification.destinataire.email:
                send_mail("ALIMMA", message, None, [notification.destinataire.email])
            fournisseur_nom = "django-email"
            cout = 0
    except Exception as exc:  # Le détail fournisseur reste uniquement en base.
        with transaction.atomic():
            notification = Notification.objects.select_for_update().get(pk=notification_id)
            notification.erreur = str(exc)[:500]
            notification.statut = (
                Notification.Statut.ECHEC
                if notification.tentatives >= MAX_TENTATIVES
                else Notification.Statut.EN_ATTENTE
            )
            notification.save(update_fields=["erreur", "statut"])
        # Le log ne contient ni numéro, ni message, ni clé d'API.
        logger.warning("Échec d'envoi de notification", extra={"notification_id": notification_id})
        if notification.statut == Notification.Statut.EN_ATTENTE:
            raise
        return

    with transaction.atomic():
        notification = Notification.objects.select_for_update().get(pk=notification_id)
        notification.statut = Notification.Statut.ENVOYEE
        notification.fournisseur = fournisseur_nom
        notification.cout_fcfa = cout
        notification.erreur = None
        notification.envoyee_at = timezone.now()
        notification.save(
            update_fields=["statut", "fournisseur", "cout_fcfa", "erreur", "envoyee_at"]
        )
