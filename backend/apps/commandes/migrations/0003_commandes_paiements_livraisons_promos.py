"""Crée les structures transactionnelles de commande, paiement et livraison."""
import apps.commandes.models
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    """Ajoute les tables strictement conformes au schéma PostgreSQL ALIMMA."""

    dependencies = [
        ("accounts", "0001_initial"),
        ("catalogue", "0006_description_trigram_index"),
        ("commandes", "0002_parametres_site_db_default"),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$ BEGIN
                CREATE TYPE statut_commande AS ENUM (
                    'attente_paiement', 'confirmee', 'payee', 'preparee',
                    'en_transit', 'livree', 'annulee', 'litige'
                );
            EXCEPTION WHEN duplicate_object THEN NULL; END $$;
            DO $$ BEGIN
                CREATE TYPE mode_paiement AS ENUM ('mobile_money', 'cod');
            EXCEPTION WHEN duplicate_object THEN NULL; END $$;
            DO $$ BEGIN
                CREATE TYPE operateur_mobile_money AS ENUM ('mtn', 'orange');
            EXCEPTION WHEN duplicate_object THEN NULL; END $$;
            DO $$ BEGIN
                CREATE TYPE statut_paiement AS ENUM ('en_attente', 'paye', 'echoue', 'rembourse');
            EXCEPTION WHEN duplicate_object THEN NULL; END $$;
            DO $$ BEGIN
                CREATE TYPE statut_livraison AS ENUM ('preparee', 'en_transit', 'livree', 'echec');
            EXCEPTION WHEN duplicate_object THEN NULL; END $$;
            DO $$ BEGIN
                CREATE TYPE type_promo AS ENUM ('globale', 'boutique');
            EXCEPTION WHEN duplicate_object THEN NULL; END $$;
            """,
            migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="Commande",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantite", models.IntegerField(default=1)),
                ("montant_produit", models.DecimalField(decimal_places=2, max_digits=12)),
                ("frais_livraison", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("montant_total", models.DecimalField(decimal_places=2, max_digits=12)),
                ("mode_paiement", apps.commandes.models.ModePaiementField(choices=[("mobile_money", "Mobile Money"), ("cod", "Paiement à la livraison")], max_length=20)),
                ("statut", apps.commandes.models.StatutCommandeField(choices=[("attente_paiement", "En attente de paiement"), ("confirmee", "Confirmée"), ("payee", "Payée"), ("preparee", "Préparée"), ("en_transit", "En transit"), ("livree", "Livrée"), ("annulee", "Annulée"), ("litige", "Litige")], default="attente_paiement", max_length=20)),
                ("adresse_livraison", models.TextField()),
                ("ville_livraison", models.CharField(max_length=100)),
                ("code_parrainage_utilise", models.CharField(blank=True, max_length=12, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("acheteur", models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name="commandes_acheteur", to="accounts.utilisateur")),
                ("annonce", models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name="commandes", to="catalogue.annonce")),
                ("vendeur", models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name="commandes_vendeur", to="accounts.utilisateur")),
            ],
            options={"db_table": "commandes"},
        ),
        migrations.AddIndex(model_name="commande", index=models.Index(fields=["acheteur"], name="idx_commandes_acheteur")),
        migrations.AddIndex(model_name="commande", index=models.Index(fields=["vendeur"], name="idx_commandes_vendeur")),
        migrations.AddIndex(model_name="commande", index=models.Index(fields=["statut"], name="idx_commandes_statut")),
        migrations.CreateModel(
            name="Paiement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("methode", apps.commandes.models.ModePaiementField(choices=[("mobile_money", "Mobile Money"), ("cod", "Paiement à la livraison")], max_length=20)),
                ("operateur", apps.commandes.models.OperateurMobileMoneyField(blank=True, choices=[("mtn", "MTN"), ("orange", "Orange")], max_length=10, null=True)),
                ("reference_transaction", models.CharField(blank=True, max_length=100, null=True)),
                ("montant", models.DecimalField(decimal_places=2, max_digits=12)),
                ("statut", apps.commandes.models.StatutPaiementField(choices=[("en_attente", "En attente"), ("paye", "Payé"), ("echoue", "Échoué"), ("rembourse", "Remboursé")], default="en_attente", max_length=20)),
                ("paye_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("commande", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="paiement", to="commandes.commande")),
            ],
            options={"db_table": "paiements"},
        ),
        migrations.CreateModel(
            name="Livraison",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("statut", apps.commandes.models.StatutLivraisonField(choices=[("preparee", "Préparée"), ("en_transit", "En transit"), ("livree", "Livrée"), ("echec", "Échec")], default="preparee", max_length=20)),
                ("qr_code", models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ("date_prise_en_charge", models.DateTimeField(blank=True, null=True)),
                ("date_livraison", models.DateTimeField(blank=True, null=True)),
                ("paiement_cod_confirme", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("commande", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="livraison", to="commandes.commande")),
                ("livreur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name="livraisons", to="accounts.utilisateur")),
            ],
            options={"db_table": "livraisons"},
        ),
        migrations.AddIndex(model_name="livraison", index=models.Index(fields=["livreur"], name="idx_livraisons_livreur")),
        migrations.AddIndex(model_name="livraison", index=models.Index(fields=["statut"], name="idx_livraisons_statut")),
        migrations.CreateModel(
            name="CodePromo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=30, unique=True)),
                ("type", apps.commandes.models.TypePromoField(choices=[("globale", "Globale"), ("boutique", "Boutique")], max_length=10)),
                ("reduction_pct", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("reduction_montant", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("date_debut", models.DateTimeField()),
                ("date_fin", models.DateTimeField()),
                ("usage_max", models.IntegerField(blank=True, null=True)),
                ("usage_actuel", models.IntegerField(default=0)),
                ("est_actif", models.BooleanField(default=True)),
                ("vendeur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name="codes_promo", to="accounts.utilisateur")),
            ],
            options={"db_table": "codes_promo"},
        ),
        migrations.AddIndex(model_name="codepromo", index=models.Index(fields=["vendeur"], name="idx_codes_promo_vendeur")),
    ]
