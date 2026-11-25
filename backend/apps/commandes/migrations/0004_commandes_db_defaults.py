"""Aligne les valeurs temporelles par défaut avec ``schema.sql``."""
import django.utils.timezone
from django.db import migrations, models
from django.db.models.functions import Now


class Migration(migrations.Migration):
    """Ajoute DEFAULT now() aux horodatages des tables transactionnelles."""

    dependencies = [("commandes", "0003_commandes_paiements_livraisons_promos")]

    operations = [
        migrations.AlterField(
            model_name="commande",
            name="created_at",
            field=models.DateTimeField(db_default=Now(), default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="commande",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, db_default=Now()),
        ),
        migrations.AlterField(
            model_name="paiement",
            name="created_at",
            field=models.DateTimeField(db_default=Now(), default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="livraison",
            name="created_at",
            field=models.DateTimeField(db_default=Now(), default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="livraison",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, db_default=Now()),
        ),
    ]
