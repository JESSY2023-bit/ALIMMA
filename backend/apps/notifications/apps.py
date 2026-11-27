"""Configuration de l'application de notifications."""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Déclare le domaine des notifications asynchrones."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
