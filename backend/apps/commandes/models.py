"""Modèles de configuration requis par le domaine commandes."""
from django.db import models
from django.db.models.functions import Now
from django.utils import timezone


class ParametreSite(models.Model):
    """Valeur configurable de la plateforme, conforme à ``parametres_site``."""

    cle = models.CharField(max_length=100, primary_key=True)
    valeur = models.TextField()
    description = models.TextField(null=True, blank=True)
    # ``db_default`` conserve aussi DEFAULT now() pour les insertions SQL directes.
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "parametres_site"
