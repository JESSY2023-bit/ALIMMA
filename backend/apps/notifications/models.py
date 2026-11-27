"""Persistance auditable des notifications envoyées aux utilisateurs."""
from django.db import models
from django.utils import timezone


class CanalNotificationField(models.CharField):
    """Champ relié au type PostgreSQL ``canal_notification`` de référence."""

    def db_type(self, connection):
        """Préserve l'énumération native PostgreSQL lors des migrations."""
        return "canal_notification"


class StatutNotificationField(models.CharField):
    """Champ relié au type PostgreSQL ``statut_notification`` de référence."""

    def db_type(self, connection):
        """Préserve l'énumération native PostgreSQL lors des migrations."""
        return "statut_notification"


class Notification(models.Model):
    """Une tentative de notification sur un canal et un gabarit déterminés."""

    class Canal(models.TextChoices):
        SMS = "sms", "SMS"
        EMAIL = "email", "E-mail"

    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        ENVOYEE = "envoyee", "Envoyée"
        ECHEC = "echec", "Échec"

    destinataire = models.ForeignKey(
        "accounts.Utilisateur",
        on_delete=models.DO_NOTHING,
        related_name="notifications",
    )
    canal = CanalNotificationField(max_length=10, choices=Canal.choices)
    gabarit = models.CharField(max_length=100)
    contexte = models.JSONField(default=dict)
    statut = StatutNotificationField(
        max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    tentatives = models.PositiveSmallIntegerField(default=0)
    cout_fcfa = models.PositiveIntegerField(default=0)
    fournisseur = models.CharField(max_length=100, null=True, blank=True)
    erreur = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    envoyee_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=["statut", "created_at"], name="idx_notif_statut_date"),
            models.Index(fields=["destinataire", "created_at"], name="idx_notif_dest_date"),
        ]
