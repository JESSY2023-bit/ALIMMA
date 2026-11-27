"""Point d'entrée métier unique pour les notifications asynchrones."""
import django_rq
from django.conf import settings
from django.db import transaction
from rq import Retry

from .models import Notification
from .tasks import MAX_TENTATIVES, envoyer_notification


def notifier(utilisateur, gabarit, contexte, canaux=(Notification.Canal.SMS,)):
    """Crée les notifications puis les place après commit dans la file RQ.

    La tâche vérifie son statut et son nombre de tentatives : une relance RQ
    ou un doublon d'exécution ne peut donc pas renvoyer une notification déjà
    marquée envoyée.
    """
    notifications = []
    for canal in canaux:
        if canal == Notification.Canal.EMAIL and not utilisateur.email:
            continue
        notification = Notification.objects.create(
            destinataire=utilisateur,
            canal=canal,
            gabarit=gabarit,
            contexte=contexte,
            cout_fcfa=settings.SMS_COST_FCFA if canal == Notification.Canal.SMS else 0,
        )
        notifications.append(notification)

        def mettre_en_file(notification_id=notification.id):
            """Enfile avec les trois essais demandés sans fermer sur un objet ORM."""
            django_rq.get_queue("default", is_async=settings.RQ_ASYNC).enqueue(
                envoyer_notification,
                notification_id,
                retry=Retry(max=MAX_TENTATIVES - 1, interval=[60, 300]),
            )

        transaction.on_commit(mettre_en_file)
    return notifications
