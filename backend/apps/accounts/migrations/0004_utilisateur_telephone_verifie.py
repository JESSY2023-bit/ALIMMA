"""Ajoute la preuve OTP et conserve l'accès des comptes antérieurs."""
from django.db import migrations, models


def verifier_comptes_existants(apps, schema_editor):
    """Évite de bloquer les comptes créés avant l'introduction de l'OTP."""
    Utilisateur = apps.get_model("accounts", "Utilisateur")
    Utilisateur.objects.filter(telephone_verifie=False).update(telephone_verifie=True)


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_utilisateur_langue")]

    operations = [
        migrations.AddField(
            model_name="utilisateur",
            name="telephone_verifie",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(verifier_comptes_existants, migrations.RunPython.noop),
    ]
