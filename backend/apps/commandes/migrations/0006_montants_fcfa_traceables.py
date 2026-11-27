"""Rend les montants FCFA entiers et traçables par commande."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Convertit les valeurs existantes avant d'ajouter les contraintes métier."""

    dependencies = [("commandes", "0005_cycle_commande_achat_direct")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE commandes
                ALTER COLUMN montant_produit TYPE BIGINT
                USING FLOOR(montant_produit)::BIGINT,
                ALTER COLUMN frais_livraison TYPE BIGINT
                USING FLOOR(frais_livraison)::BIGINT,
                ALTER COLUMN montant_total TYPE BIGINT
                USING FLOOR(montant_total)::BIGINT;
            ALTER TABLE paiements
                ALTER COLUMN montant TYPE BIGINT
                USING FLOOR(montant)::BIGINT;
            ALTER TABLE codes_promo
                ALTER COLUMN reduction_montant TYPE BIGINT
                USING FLOOR(reduction_montant)::BIGINT;
            """,
            migrations.RunSQL.noop,
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="commande",
                    name="montant_produit",
                    field=models.PositiveBigIntegerField(),
                ),
                migrations.AlterField(
                    model_name="commande",
                    name="frais_livraison",
                    field=models.PositiveBigIntegerField(default=0),
                ),
                migrations.AlterField(
                    model_name="commande",
                    name="montant_total",
                    field=models.PositiveBigIntegerField(),
                ),
                migrations.AlterField(
                    model_name="paiement",
                    name="montant",
                    field=models.PositiveBigIntegerField(),
                ),
                migrations.AlterField(
                    model_name="codepromo",
                    name="reduction_montant",
                    field=models.PositiveBigIntegerField(blank=True, null=True),
                ),
            ],
        ),
        migrations.AddField(
            model_name="commande",
            name="montant_reduction",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="commande",
            name="code_promo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="commandes",
                to="commandes.codepromo",
            ),
        ),
        migrations.RunSQL(
            """
            UPDATE commandes
            SET montant_reduction = GREATEST(
                montant_produit + frais_livraison - montant_total,
                0
            );
            """,
            migrations.RunSQL.noop,
        ),
        migrations.AddConstraint(
            model_name="commande",
            constraint=models.CheckConstraint(
                condition=models.Q(montant_reduction__lte=models.F("montant_produit")),
                name="commandes_reduction_plafonnee",
            ),
        ),
        migrations.AddConstraint(
            model_name="commande",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    montant_total=(
                        models.F("montant_produit")
                        - models.F("montant_reduction")
                        + models.F("frais_livraison")
                    )
                ),
                name="commandes_total_traceable",
            ),
        ),
    ]
