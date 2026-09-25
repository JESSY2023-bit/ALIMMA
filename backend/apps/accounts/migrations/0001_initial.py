"""Création des utilisateurs et parrainages conformes au schéma ALIMMA."""
from decimal import Decimal

import apps.accounts.models
import django.db.models.deletion
import django.utils.timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(
            """
            CREATE TYPE role_utilisateur AS ENUM (
                'utilisateur', 'vendeur_pro', 'moderateur', 'livreur', 'administrateur'
            );
            """,
            migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="Utilisateur",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=150)),
                ("email", models.EmailField(blank=True, max_length=255, null=True, unique=True)),
                ("telephone", models.CharField(max_length=20, unique=True)),
                ("password_hash", models.CharField(max_length=255)),
                ("role", apps.accounts.models.RoleUtilisateurField(choices=[("utilisateur", "Utilisateur"), ("vendeur_pro", "Vendeur pro"), ("moderateur", "Modérateur"), ("livreur", "Livreur"), ("administrateur", "Administrateur")], default="utilisateur", max_length=20)),
                ("photo_url", models.TextField(blank=True, null=True)),
                ("note_moyenne", models.DecimalField(decimal_places=1, default=Decimal("0.0"), max_digits=2, validators=[MinValueValidator(0), MaxValueValidator(5)])),
                ("nb_avis", models.IntegerField(default=0)),
                ("points_parrainage", models.IntegerField(default=0)),
                ("code_parrainage", models.CharField(default=apps.accounts.models.generate_referral_code, max_length=12, unique=True)),
                ("deux_fa_active", models.BooleanField(default=False)),
                ("est_actif", models.BooleanField(default=True)),
                ("derniere_connexion", models.DateTimeField(blank=True, null=True)),
                ("date_inscription", models.DateTimeField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("parraine_par", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name="filleuls", to="accounts.utilisateur")),
            ],
            options={
                "db_table": "utilisateurs",
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            note_moyenne__gte=0,
                            note_moyenne__lte=5,
                        ),
                        name="utilisateurs_note_moyenne_entre_0_et_5",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Parrainage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recompense_utilisee", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("filleul", models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name="parrainage_recu", to="accounts.utilisateur")),
                ("parrain", models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name="parrainages", to="accounts.utilisateur")),
            ],
            options={"db_table": "parrainages"},
        ),
    ]
