"""Crée la persistance auditable des notifications."""
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import apps.notifications.models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0003_utilisateur_langue")]

    operations = [
        migrations.RunSQL(
            "CREATE TYPE canal_notification AS ENUM ('sms', 'email');"
            "CREATE TYPE statut_notification AS ENUM ('en_attente', 'envoyee', 'echec');",
            "DROP TYPE statut_notification; DROP TYPE canal_notification;",
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("canal", apps.notifications.models.CanalNotificationField(choices=[("sms", "SMS"), ("email", "E-mail")], max_length=10)),
                ("gabarit", models.CharField(max_length=100)),
                ("contexte", models.JSONField(default=dict)),
                ("statut", apps.notifications.models.StatutNotificationField(choices=[("en_attente", "En attente"), ("envoyee", "Envoyée"), ("echec", "Échec")], default="en_attente", max_length=20)),
                ("tentatives", models.PositiveSmallIntegerField(default=0)),
                ("cout_fcfa", models.PositiveIntegerField(default=0)),
                ("fournisseur", models.CharField(blank=True, max_length=100, null=True)),
                ("erreur", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("envoyee_at", models.DateTimeField(blank=True, null=True)),
                ("destinataire", models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name="notifications", to="accounts.utilisateur")),
            ],
            options={
                "db_table": "notifications",
                "indexes": [
                    models.Index(fields=["statut", "created_at"], name="idx_notif_statut_date"),
                    models.Index(fields=["destinataire", "created_at"], name="idx_notif_dest_date"),
                ],
            },
        )
    ]
