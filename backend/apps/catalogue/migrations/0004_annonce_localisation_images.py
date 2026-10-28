"""Ajoute la géolocalisation PostGIS et les images ordonnées des annonces."""
from django.contrib.postgres.indexes import GistIndex
import apps.catalogue.models
from django.contrib.postgres.operations import CreateExtension
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalogue", "0003_remove_postgis_extension")]

    operations = [
        CreateExtension("postgis"),
        migrations.AddField(
            model_name="annonce",
            name="localisation",
            field=apps.catalogue.models.GeographyPointField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="annonce",
            index=GistIndex(fields=["localisation"], name="idx_annonces_localisation_gist"),
        ),
        migrations.CreateModel(
            name="AnnonceImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.TextField()),
                ("ordre", models.SmallIntegerField(default=0)),
                ("annonce", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="catalogue.annonce")),
            ],
            options={"db_table": "annonce_images", "ordering": ("ordre", "id")},
        ),
        migrations.AddIndex(
            model_name="annonceimage",
            index=models.Index(fields=["annonce"], name="idx_annonce_images_annonce"),
        ),
    ]
