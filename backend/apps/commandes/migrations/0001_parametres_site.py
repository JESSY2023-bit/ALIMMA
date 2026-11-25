"""Crée la table de paramètres configurables du site."""
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    """Ajoute ``parametres_site`` conformément au schéma de référence."""

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ParametreSite",
            fields=[
                ("cle", models.CharField(max_length=100, primary_key=True, serialize=False)),
                ("valeur", models.TextField()),
                ("description", models.TextField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={"db_table": "parametres_site"},
        ),
    ]
