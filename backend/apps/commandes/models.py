"""Modèles de panier, commandes, paiements et livraisons ALIMMA."""
from django.db import models
from django.db.models.functions import Now
from django.utils import timezone


class ParametreSite(models.Model):
    """Valeur configurable de la plateforme, conforme à ``parametres_site``."""

    cle = models.CharField(max_length=100, primary_key=True)
    valeur = models.TextField()
    description = models.TextField(null=True, blank=True)
    # ``db_default`` conserve aussi DEFAULT now() pour les insertions SQL directes.
    updated_at = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "parametres_site"


class StatutCommandeField(models.CharField):
    """Préserve le type PostgreSQL ``statut_commande`` du schéma de référence."""

    def db_type(self, connection):
        """Empêche Django de remplacer l'énumération par un varchar."""
        return "statut_commande"


class ModeRemiseField(models.CharField):
    """Préserve l'énumération PostgreSQL ``mode_remise``."""

    def db_type(self, connection):
        """Déclare le type enum utilisé par l'adresse structurée."""
        return "mode_remise"


class ModePaiementField(models.CharField):
    """Préserve le type PostgreSQL ``mode_paiement`` du schéma de référence."""

    def db_type(self, connection):
        """Déclare l'énumération PostgreSQL imposée au stockage."""
        return "mode_paiement"


class OperateurMobileMoneyField(models.CharField):
    """Préserve le type PostgreSQL ``operateur_mobile_money``."""

    def db_type(self, connection):
        """Déclare le type enum de l'opérateur de paiement."""
        return "operateur_mobile_money"


class StatutPaiementField(models.CharField):
    """Préserve le type PostgreSQL ``statut_paiement``."""

    def db_type(self, connection):
        """Déclare l'énumération de paiement dans PostgreSQL."""
        return "statut_paiement"


class StatutLivraisonField(models.CharField):
    """Préserve le type PostgreSQL ``statut_livraison``."""

    def db_type(self, connection):
        """Déclare l'énumération de livraison dans PostgreSQL."""
        return "statut_livraison"


class TypePromoField(models.CharField):
    """Préserve le type PostgreSQL ``type_promo`` pour les codes promotionnels."""

    def db_type(self, connection):
        """Déclare l'énumération de promotion dans PostgreSQL."""
        return "type_promo"


class Commande(models.Model):
    """Achat atomique d'une annonce par un utilisateur distinct du vendeur."""

    class ModePaiement(models.TextChoices):
        MOBILE_MONEY = "mobile_money", "Mobile Money"
        COD = "cod", "Paiement à la livraison"

    class Statut(models.TextChoices):
        ATTENTE_PAIEMENT = "attente_paiement", "En attente de paiement"
        ATTENTE_VENDEUR = "attente_vendeur", "En attente du vendeur"
        ACCEPTEE = "acceptee", "Acceptée"
        EXPEDIEE = "expediee", "Expédiée"
        LIVREE = "livree", "Livrée"
        ECHEC_LIVRAISON = "echec_livraison", "Échec de livraison"
        LITIGE = "litige", "Litige"
        TERMINEE = "terminee", "Terminée"
        ANNULEE = "annulee", "Annulée"
        REMBOURSEE = "remboursee", "Remboursée"

    class ModeRemise(models.TextChoices):
        MAIN_PROPRE = "main_propre", "Remise en main propre"
        LIVRAISON_VENDEUR = "livraison_vendeur", "Livraison par le vendeur"

    acheteur = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.DO_NOTHING, related_name="commandes_acheteur"
    )
    annonce = models.ForeignKey(
        "catalogue.Annonce", on_delete=models.DO_NOTHING, related_name="commandes"
    )
    vendeur = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.DO_NOTHING, related_name="commandes_vendeur"
    )
    quantite = models.IntegerField(default=1)
    montant_produit = models.DecimalField(max_digits=12, decimal_places=2)
    frais_livraison = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)
    mode_paiement = ModePaiementField(max_length=20, choices=ModePaiement.choices)
    statut = StatutCommandeField(
        max_length=20, choices=Statut.choices, default=Statut.ATTENTE_PAIEMENT
    )
    mode_remise = ModeRemiseField(max_length=20, choices=ModeRemise.choices)
    ville = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100)
    repere = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    telephone_contact = models.CharField(max_length=20)
    code_parrainage_utilise = models.CharField(max_length=12, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        db_table = "commandes"
        indexes = [
            models.Index(fields=["acheteur"], name="idx_commandes_acheteur"),
            models.Index(fields=["vendeur"], name="idx_commandes_vendeur"),
            models.Index(fields=["statut"], name="idx_commandes_statut"),
        ]


class HistoriqueStatutCommande(models.Model):
    """Trace immuable des changements d'état d'une commande."""

    commande = models.ForeignKey(
        Commande, on_delete=models.CASCADE, related_name="historique_statuts"
    )
    ancien_statut = StatutCommandeField(max_length=20, choices=Commande.Statut.choices)
    nouveau_statut = StatutCommandeField(max_length=20, choices=Commande.Statut.choices)
    acteur = models.ForeignKey(
        "accounts.Utilisateur",
        on_delete=models.DO_NOTHING,
        related_name="transitions_commandes",
        null=True,
        blank=True,
    )
    motif = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "historique_statuts_commandes"
        ordering = ("created_at", "id")
        indexes = [
            models.Index(fields=["commande", "created_at"], name="idx_hist_cmd_date"),
        ]


class Paiement(models.Model):
    """Paiement unique d'une commande, créé avec celle-ci dans la transaction."""

    class Operateur(models.TextChoices):
        MTN = "mtn", "MTN"
        ORANGE = "orange", "Orange"

    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        PAYE = "paye", "Payé"
        ECHOUE = "echoue", "Échoué"
        REMBOURSE = "rembourse", "Remboursé"

    commande = models.OneToOneField(
        Commande, on_delete=models.CASCADE, related_name="paiement"
    )
    methode = ModePaiementField(max_length=20, choices=Commande.ModePaiement.choices)
    operateur = OperateurMobileMoneyField(
        max_length=10, choices=Operateur.choices, null=True, blank=True
    )
    reference_transaction = models.CharField(max_length=100, null=True, blank=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    statut = StatutPaiementField(
        max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    paye_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "paiements"


class Livraison(models.Model):
    """Livraison unique et traçable associée à une commande confirmée."""

    class Statut(models.TextChoices):
        PREPAREE = "preparee", "Préparée"
        EN_TRANSIT = "en_transit", "En transit"
        LIVREE = "livree", "Livrée"
        ECHEC = "echec", "Échec"

    commande = models.OneToOneField(
        Commande, on_delete=models.CASCADE, related_name="livraison"
    )
    livreur = models.ForeignKey(
        "accounts.Utilisateur",
        on_delete=models.DO_NOTHING,
        related_name="livraisons",
        null=True,
        blank=True,
    )
    statut = StatutLivraisonField(
        max_length=20, choices=Statut.choices, default=Statut.PREPAREE
    )
    qr_code = models.CharField(max_length=64, unique=True, null=True, blank=True)
    date_prise_en_charge = models.DateTimeField(null=True, blank=True)
    date_livraison = models.DateTimeField(null=True, blank=True)
    paiement_cod_confirme = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        db_table = "livraisons"
        indexes = [
            models.Index(fields=["livreur"], name="idx_livraisons_livreur"),
            models.Index(fields=["statut"], name="idx_livraisons_statut"),
        ]


class CodePromo(models.Model):
    """Code promotionnel global ou réservé aux annonces d'un vendeur."""

    class Type(models.TextChoices):
        GLOBALE = "globale", "Globale"
        BOUTIQUE = "boutique", "Boutique"

    code = models.CharField(max_length=30, unique=True)
    type = TypePromoField(max_length=10, choices=Type.choices)
    vendeur = models.ForeignKey(
        "accounts.Utilisateur",
        on_delete=models.DO_NOTHING,
        related_name="codes_promo",
        null=True,
        blank=True,
    )
    reduction_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reduction_montant = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    usage_max = models.IntegerField(null=True, blank=True)
    usage_actuel = models.IntegerField(default=0)
    est_actif = models.BooleanField(default=True)

    class Meta:
        db_table = "codes_promo"
        indexes = [models.Index(fields=["vendeur"], name="idx_codes_promo_vendeur")]
