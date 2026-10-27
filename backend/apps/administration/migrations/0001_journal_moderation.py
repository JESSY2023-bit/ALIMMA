"""Crée le journal d'audit des actions de modération."""
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0002_profils_roles")]

    operations = [
        migrations.CreateModel(
            name="JournalModeration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=100)),
                ("cible_type", models.CharField(max_length=50)),
                ("cible_id", models.BigIntegerField()),
                ("details", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("moderateur", models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name="actions_moderation", to="accounts.utilisateur")),
            ],
            options={"db_table": "journal_moderation"},
        ),
    ]
