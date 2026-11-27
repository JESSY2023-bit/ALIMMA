"""Interface de notification conservée pour la modération existante."""
from apps.notifications.services import notifier


class NotificationService:
    """Adapte l'ancien contrat de modération au domaine notifications."""

    @staticmethod
    def notifier_decision_annonce(*, vendeur, annonce, decision, motif):
        """Programme une information du vendeur après une décision humaine."""
        gabarit = "annonce_validee" if decision == "valider" else "annonce_rejetee"
        return notifier(
            vendeur,
            gabarit,
            {"titre": annonce.titre, "motif": motif or "-"},
            canaux=("sms", "email"),
        )
