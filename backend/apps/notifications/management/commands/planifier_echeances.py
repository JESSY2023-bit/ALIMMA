"""Enregistre les travaux récurrents indispensables au worker RQ."""
from django.core.management.base import BaseCommand
from django_rq import get_scheduler

from apps.notifications.jobs import traiter_echeances_commandes


class Command(BaseCommand):
    """Crée ou actualise le traitement des échéances toutes les cinq minutes."""

    help = "Planifie le traitement des échéances de commande toutes les 5 minutes."

    def handle(self, *args, **options):
        """Utilise un identifiant fixe pour que la commande reste idempotente."""
        scheduler = get_scheduler("default")
        scheduler.cron(
            "*/5 * * * *",
            func=traiter_echeances_commandes,
            id="traiter-echeances-commandes",
            queue_name="default",
            repeat=None,
        )
        self.stdout.write(self.style.SUCCESS("Échéances de commandes planifiées."))
