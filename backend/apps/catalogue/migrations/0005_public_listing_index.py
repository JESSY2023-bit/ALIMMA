"""Optimise le filtre et le tri de la liste publique des annonces."""
from django.db import migrations, models


class Migration(migrations.Migration):
    """Ajoute l'index composite justifié par la liste publique la plus fréquente."""

    dependencies = [("catalogue", "0004_annonce_localisation_images")]

    operations = [
        migrations.AddIndex(
            model_name="annonce",
            index=models.Index(
                fields=["statut", "-date_publication"],
                name="idx_ann_statut_pub",
            ),
        ),
    ]
