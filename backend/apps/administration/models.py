"""Modèles de l'administration fonctionnelle."""
from django.db import models
from django.utils import timezone


class JournalModeration(models.Model):
    """Trace immuable des actions d'administration et de modération."""

    moderateur = models.ForeignKey(
        "accounts.Utilisateur",
        on_delete=models.DO_NOTHING,
        related_name="actions_moderation",
    )
    action = models.CharField(max_length=100)
    cible_type = models.CharField(max_length=50)
    cible_id = models.BigIntegerField()
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "journal_moderation"
