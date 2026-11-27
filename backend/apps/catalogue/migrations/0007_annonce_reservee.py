"""Ajoute l'état de réservation d'une annonce pendant un achat direct."""
import apps.catalogue.models
from django.db import migrations


class Migration(migrations.Migration):
    """Préserve l'enum PostgreSQL et l'état Django de ``statut_annonce``."""

    dependencies = [("catalogue", "0006_description_trigram_index")]

    operations = [
        migrations.RunSQL(
            "ALTER TYPE statut_annonce ADD VALUE IF NOT EXISTS 'reservee';",
            migrations.RunSQL.noop,
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="annonce",
                    name="statut",
                    field=apps.catalogue.models.StatutAnnonceField(
                        choices=[
                            ("en_attente_moderation", "En attente de modération"),
                            ("active", "Active"),
                            ("reservee", "Réservée"),
                            ("en_pause", "En pause"),
                            ("rejetee", "Rejetée"),
                            ("vendue", "Vendue"),
                            ("expiree", "Expirée"),
                        ],
                        default="en_attente_moderation",
                        max_length=25,
                    ),
                ),
            ],
        ),
    ]
