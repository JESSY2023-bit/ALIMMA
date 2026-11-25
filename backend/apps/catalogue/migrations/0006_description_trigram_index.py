"""Indexe les descriptions pour la recherche approximative PostgreSQL."""
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):
    """Ajoute l'index pg_trgm couvrant les descriptions d'annonces."""

    dependencies = [("catalogue", "0005_public_listing_index")]

    operations = [
        migrations.AddIndex(
            model_name="annonce",
            index=GinIndex(
                fields=["description"],
                name="idx_ann_desc_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
