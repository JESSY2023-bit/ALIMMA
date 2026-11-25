"""Aligne le défaut PostgreSQL de ``parametres_site.updated_at``."""
import django.utils.timezone
from django.db import migrations, models
from django.db.models.functions import Now


class Migration(migrations.Migration):
    """Conserve DEFAULT now() pour les insertions qui ne passent pas par Django."""

    dependencies = [("commandes", "0001_parametres_site")]

    operations = [
        migrations.AlterField(
            model_name="parametresite",
            name="updated_at",
            field=models.DateTimeField(db_default=Now(), default=django.utils.timezone.now),
        ),
    ]
