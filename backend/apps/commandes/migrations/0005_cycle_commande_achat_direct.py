"""Fait évoluer les commandes vers le cycle d'achat direct ALIMMA."""
import apps.commandes.models
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models
from django.db.models.functions import Now


STATUTS_COMMANDE = """
    'attente_paiement', 'attente_vendeur', 'acceptee', 'expediee',
    'livree', 'echec_livraison', 'litige', 'terminee', 'annulee', 'remboursee'
"""
COMMANDE_CHOICES = [
    ("attente_paiement", "En attente de paiement"),
    ("attente_vendeur", "En attente du vendeur"),
    ("acceptee", "Acceptée"),
    ("expediee", "Expédiée"),
    ("livree", "Livrée"),
    ("echec_livraison", "Échec de livraison"),
    ("litige", "Litige"),
    ("terminee", "Terminée"),
    ("annulee", "Annulée"),
    ("remboursee", "Remboursée"),
]


class Migration(migrations.Migration):
    """Convertit les données existantes sans supprimer l'historique métier."""

    dependencies = [
        ("accounts", "0001_initial"),
        ("catalogue", "0007_annonce_reservee"),
        ("commandes", "0004_commandes_db_defaults"),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TYPE statut_commande RENAME TO statut_commande_ancien;
            CREATE TYPE statut_commande AS ENUM (""" + STATUTS_COMMANDE + """);
            ALTER TABLE commandes ALTER COLUMN statut DROP DEFAULT;
            ALTER TABLE commandes
                ALTER COLUMN statut TYPE statut_commande
                USING (
                    CASE statut::text
                        WHEN 'confirmee' THEN 'attente_vendeur'
                        WHEN 'payee' THEN 'attente_vendeur'
                        WHEN 'preparee' THEN 'acceptee'
                        WHEN 'en_transit' THEN 'expediee'
                        ELSE statut::text
                    END
                )::statut_commande;
            ALTER TABLE commandes
                ALTER COLUMN statut SET DEFAULT 'attente_paiement'::statut_commande;
            DROP TYPE statut_commande_ancien;

            CREATE TYPE mode_remise AS ENUM ('main_propre', 'livraison_vendeur');
            """,
            """
            -- La migration inverse est volontairement non destructive : PostgreSQL
            -- ne peut retirer une valeur d'enum sans recréer le type complet.
            """,
        ),
        # Le SQL précédent modifie déjà la colonne ; cette opération aligne
        # uniquement l'état Django afin que makemigrations --check reste vert.
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="commande",
                    name="statut",
                    field=apps.commandes.models.StatutCommandeField(
                        choices=COMMANDE_CHOICES,
                        default="attente_paiement",
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="commande",
            name="mode_remise",
            field=apps.commandes.models.ModeRemiseField(
                choices=[
                    ("main_propre", "Remise en main propre"),
                    ("livraison_vendeur", "Livraison par le vendeur"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="commande",
            name="ville",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="commande",
            name="quartier",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="commande",
            name="repere",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="commande",
            name="latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="commande",
            name="longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="commande",
            name="telephone_contact",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.RunSQL(
            """
            UPDATE commandes
            SET mode_remise = 'livraison_vendeur'::mode_remise,
                ville = ville_livraison,
                quartier = 'Non renseigné',
                repere = LEFT(adresse_livraison, 200),
                telephone_contact = (
                    SELECT telephone FROM utilisateurs
                    WHERE utilisateurs.id = commandes.acheteur_id
                );
            """,
            migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name="commande",
            name="mode_remise",
            field=apps.commandes.models.ModeRemiseField(
                choices=[
                    ("main_propre", "Remise en main propre"),
                    ("livraison_vendeur", "Livraison par le vendeur"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="commande",
            name="ville",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="commande",
            name="quartier",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="commande",
            name="repere",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="commande",
            name="telephone_contact",
            field=models.CharField(max_length=20),
        ),
        migrations.RemoveField(model_name="commande", name="adresse_livraison"),
        migrations.RemoveField(model_name="commande", name="ville_livraison"),
        migrations.CreateModel(
            name="HistoriqueStatutCommande",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ancien_statut",
                    apps.commandes.models.StatutCommandeField(
                        choices=COMMANDE_CHOICES, max_length=20
                    ),
                ),
                (
                    "nouveau_statut",
                    apps.commandes.models.StatutCommandeField(
                        choices=COMMANDE_CHOICES, max_length=20
                    ),
                ),
                ("motif", models.TextField(blank=True, null=True)),
                (
                    "created_at",
                    models.DateTimeField(
                        db_default=Now(), default=django.utils.timezone.now
                    ),
                ),
                (
                    "acteur",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="transitions_commandes",
                        to="accounts.utilisateur",
                    ),
                ),
                (
                    "commande",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historique_statuts",
                        to="commandes.commande",
                    ),
                ),
            ],
            options={"db_table": "historique_statuts_commandes", "ordering": ("created_at", "id")},
        ),
        migrations.AddIndex(
            model_name="historiquestatutcommande",
            index=models.Index(fields=["commande", "created_at"], name="idx_hist_cmd_date"),
        ),
    ]
