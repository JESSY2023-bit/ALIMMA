"""Crée les catégories et annonces minimales définies dans le schéma ALIMMA."""
from decimal import Decimal

import apps.catalogue.models
import django.contrib.gis.db.models.fields
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    """Ajoute les deux tables catalogue nécessaires à l'activité de vente."""

    dependencies = [
        ("accounts", "0001_initial"),
        ("catalogue", "0001_enable_extensions"),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE TYPE type_vente AS ENUM ('fixe', 'enchere');",
            "DROP TYPE IF EXISTS type_vente;",
        ),
        migrations.RunSQL(
            "CREATE TYPE etat_produit AS ENUM ('neuf', 'occasion');",
            "DROP TYPE IF EXISTS etat_produit;",
        ),
        migrations.RunSQL(
            """
            CREATE TYPE statut_annonce AS ENUM (
                'en_attente_moderation', 'active', 'en_pause', 'rejetee', 'vendue', 'expiree'
            );
            """,
            "DROP TYPE IF EXISTS statut_annonce;",
        ),
        migrations.CreateModel(
            name="Categorie",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=100)),
                ("slug", models.CharField(max_length=120, unique=True)),
                ("icone_url", models.TextField(blank=True, null=True)),
                ("ordre_affichage", models.IntegerField(default=0)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name="enfants", to="catalogue.categorie")),
            ],
            options={"db_table": "categories"},
        ),
        migrations.AddIndex(
            model_name="categorie",
            index=models.Index(fields=["parent"], name="idx_categories_parent"),
        ),
        migrations.CreateModel(
            name="Annonce",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titre", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("prix", models.DecimalField(decimal_places=2, max_digits=12)),
                ("type_vente", apps.catalogue.models.TypeVenteField(choices=[("fixe", "Fixe"), ("enchere", "Enchère")], default="fixe", max_length=10)),
                ("etat", apps.catalogue.models.EtatProduitField(choices=[("neuf", "Neuf"), ("occasion", "Occasion")], default="occasion", max_length=10)),
                ("ville", models.CharField(max_length=100)),
                ("quartier", models.CharField(blank=True, max_length=100, null=True)),
                ("localisation", django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ("statut", apps.catalogue.models.StatutAnnonceField(choices=[("en_attente_moderation", "En attente de modération"), ("active", "Active"), ("en_pause", "En pause"), ("rejetee", "Rejetée"), ("vendue", "Vendue"), ("expiree", "Expirée")], default="en_attente_moderation", max_length=25)),
                ("nb_vues", models.IntegerField(default=0)),
                ("date_publication", models.DateTimeField(blank=True, null=True)),
                ("date_expiration", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("categorie", models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name="annonces", to="catalogue.categorie")),
                ("vendeur", models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name="annonces", to="accounts.utilisateur")),
            ],
            options={
                "db_table": "annonces",
                "constraints": [
                    models.CheckConstraint(condition=models.Q(("prix__gte", Decimal("0"))), name="annonces_prix_positif"),
                ],
            },
        ),
        migrations.AddIndex(model_name="annonce", index=models.Index(fields=["vendeur"], name="idx_annonces_vendeur")),
        migrations.AddIndex(model_name="annonce", index=models.Index(fields=["categorie"], name="idx_annonces_categorie")),
        migrations.AddIndex(model_name="annonce", index=models.Index(fields=["statut"], name="idx_annonces_statut")),
        migrations.RunSQL(
            "CREATE INDEX idx_annonces_localisation ON annonces USING GIST (localisation);",
            "DROP INDEX IF EXISTS idx_annonces_localisation;",
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_annonces_titre_trgm ON annonces USING GIN (titre gin_trgm_ops);",
            "DROP INDEX IF EXISTS idx_annonces_titre_trgm;",
        ),
    ]
