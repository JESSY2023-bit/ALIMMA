"""Ajoute les profils liés aux rôles vendeur pro et livreur."""
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="ProfilVendeurPro",
            fields=[
                ("utilisateur", models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name="profil_vendeur_pro", serialize=False, to="accounts.utilisateur")),
                ("siret_niu", models.CharField(blank=True, max_length=50, null=True)),
                ("nom_boutique", models.CharField(max_length=150)),
                ("logo_url", models.TextField(blank=True, null=True)),
                ("banniere_url", models.TextField(blank=True, null=True)),
                ("description_boutique", models.TextField(blank=True, null=True)),
                ("nb_ventes_total", models.IntegerField(default=0)),
                ("est_certifie", models.BooleanField(default=False)),
                ("date_activation", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={"db_table": "profils_vendeur_pro"},
        ),
        migrations.CreateModel(
            name="ProfilLivreur",
            fields=[
                ("utilisateur", models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name="profil_livreur", serialize=False, to="accounts.utilisateur")),
                ("vehicule_info", models.CharField(blank=True, max_length=100, null=True)),
                ("zone_geographique", models.CharField(blank=True, max_length=150, null=True)),
                ("statut_disponibilite", models.CharField(choices=[("disponible", "Disponible"), ("en_tournee", "En tournée"), ("hors_ligne", "Hors ligne")], default="disponible", max_length=20)),
            ],
            options={"db_table": "profils_livreur"},
        ),
    ]
