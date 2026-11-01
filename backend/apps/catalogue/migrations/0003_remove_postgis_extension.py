"""Marque la fin de la transition historique de géolocalisation."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0002_categories_annonces"),
    ]

    # Les schémas actuels utilisent uniquement latitude/longitude.
    operations = []
