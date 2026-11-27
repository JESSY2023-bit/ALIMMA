"""Fonctions planifiées par RQ Scheduler."""
from django.core.management import call_command


def traiter_echeances_commandes():
    """Délègue les échéances à la commande idempotente déjà testée du domaine."""
    call_command("traiter_echeances_commandes")
