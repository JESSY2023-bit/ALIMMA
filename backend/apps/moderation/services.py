"""Interfaces de services externes utilisés par la modération."""


class NotificationService:
    """Point d'extension pour les notifications vendeur, sans transport au MVP."""

    @staticmethod
    def notifier_decision_annonce(*, vendeur, annonce, decision, motif):
        """Expose le contrat d'envoi qui sera relié ultérieurement à un fournisseur."""
        # Aucun envoi n'est réalisé pour le MVP. Cette interface permet de
        # brancher SMS, email ou push sans modifier la logique de modération.
        return None
