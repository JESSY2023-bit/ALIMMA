"""Annule les commandes dont le vendeur ou le paiement n'a pas répondu à temps."""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.commandes.etats import TransitionInvalide, transitionner
from apps.commandes.models import Commande


class Command(BaseCommand):
    """Commande idempotente à déclencher périodiquement par le futur worker A6."""

    help = "Annule les commandes dont une échéance métier est dépassée."

    def handle(self, *args, **options):
        """Traite les deux délais en s'appuyant sur la machine d'états."""
        maintenant = timezone.now()
        regles = (
            (Commande.Statut.ATTENTE_PAIEMENT, timedelta(minutes=15), "Paiement expiré."),
            (Commande.Statut.ATTENTE_VENDEUR, timedelta(hours=24), "Réponse vendeur expirée."),
        )
        total = 0
        for statut, delai, motif in regles:
            commandes = Commande.objects.filter(
                statut=statut,
                created_at__lt=maintenant - delai,
            )
            for commande in commandes.iterator():
                try:
                    transitionner(commande, Commande.Statut.ANNULEE, None, motif)
                except TransitionInvalide:
                    # Une autre tâche a déjà traité la commande : l'opération
                    # reste idempotente et le prochain passage ne la reverra pas.
                    continue
                total += 1
        self.stdout.write(self.style.SUCCESS(f"{total} commande(s) expirée(s) traitée(s)."))
