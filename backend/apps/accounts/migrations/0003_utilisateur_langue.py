"""Ajoute la langue de communication des utilisateurs."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_profils_roles")]

    operations = [
        migrations.AddField(
            model_name="utilisateur",
            name="langue",
            field=models.CharField(
                choices=[("fr", "Français"), ("en", "English")],
                default="fr",
                max_length=2,
            ),
        )
    ]
