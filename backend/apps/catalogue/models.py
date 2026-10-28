"""Modèles de catégories et d'annonces conformes au schéma PostgreSQL ALIMMA."""
from decimal import Decimal

from django.db import models
from django.contrib.postgres.indexes import GistIndex
from django.utils import timezone


class TypeVenteField(models.CharField):
    """Champ lié au type PostgreSQL ``type_vente`` du schéma de référence."""

    def db_type(self, connection):
        """Empêche Django de remplacer l'enum PostgreSQL par un varchar."""
        return "type_vente"


class EtatProduitField(models.CharField):
    """Champ lié au type PostgreSQL ``etat_produit`` du schéma de référence."""

    def db_type(self, connection):
        """Préserve le type enum PostgreSQL lors des migrations."""
        return "etat_produit"


class StatutAnnonceField(models.CharField):
    """Champ lié au type PostgreSQL ``statut_annonce`` du schéma de référence."""

    def db_type(self, connection):
        """Préserve le type enum PostgreSQL lors des migrations."""
        return "statut_annonce"


class GeographyPointField(models.Field):
    """Champ PostGIS léger stockant exactement ``GEOGRAPHY(POINT, 4326)``.

    Le projet ne dépend pas de GeoDjango/GDAL : les écritures utilisent le WKT
    standard ``SRID=4326;POINT(longitude latitude)`` et PostGIS fait le reste.
    """

    def db_type(self, connection):
        """Déclare le type géographique imposé par l'US et l'index GiST."""
        return "geography(POINT,4326)"

    def get_internal_type(self):
        """Utilise les conversions de valeur textuelle de Django."""
        return "TextField"


class Categorie(models.Model):
    """Catégorie d'une annonce, éventuellement rattachée à une catégorie parente."""

    nom = models.CharField(max_length=100)
    slug = models.CharField(max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="enfants",
    )
    icone_url = models.TextField(null=True, blank=True)
    ordre_affichage = models.IntegerField(default=0)

    class Meta:
        db_table = "categories"
        indexes = [models.Index(fields=["parent"], name="idx_categories_parent")]


class Annonce(models.Model):
    """Annonce publiée par un utilisateur dans une catégorie du catalogue."""

    class TypeVente(models.TextChoices):
        FIXE = "fixe", "Fixe"
        ENCHERE = "enchere", "Enchère"

    class Etat(models.TextChoices):
        NEUF = "neuf", "Neuf"
        OCCASION = "occasion", "Occasion"

    class Statut(models.TextChoices):
        EN_ATTENTE_MODERATION = "en_attente_moderation", "En attente de modération"
        ACTIVE = "active", "Active"
        EN_PAUSE = "en_pause", "En pause"
        REJETEE = "rejetee", "Rejetée"
        VENDUE = "vendue", "Vendue"
        EXPIREE = "expiree", "Expirée"

    vendeur = models.ForeignKey(
        "accounts.Utilisateur",
        on_delete=models.DO_NOTHING,
        related_name="annonces",
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.DO_NOTHING,
        related_name="annonces",
    )
    titre = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    type_vente = TypeVenteField(
        max_length=10,
        choices=TypeVente.choices,
        default=TypeVente.FIXE,
    )
    etat = EtatProduitField(
        max_length=10,
        choices=Etat.choices,
        default=Etat.OCCASION,
    )
    ville = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    # La géographie reste nullable : une annonce peut être publiée sans position.
    localisation = GeographyPointField(null=True, blank=True)
    statut = StatutAnnonceField(
        max_length=25,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE_MODERATION,
    )
    nb_vues = models.IntegerField(default=0)
    date_publication = models.DateTimeField(null=True, blank=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "annonces"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(prix__gte=Decimal("0")),
                name="annonces_prix_positif",
            )
        ]
        indexes = [
            models.Index(fields=["vendeur"], name="idx_annonces_vendeur"),
            models.Index(fields=["categorie"], name="idx_annonces_categorie"),
            models.Index(fields=["statut"], name="idx_annonces_statut"),
            models.Index(
                fields=["latitude", "longitude"],
                name="idx_annonces_coordinates",
            ),
            GistIndex(fields=["localisation"], name="idx_annonces_localisation_gist"),
        ]


class AnnonceImage(models.Model):
    """Image stockée d'une annonce, avec l'ordre explicite demandé par le contrat."""

    annonce = models.ForeignKey(
        Annonce,
        on_delete=models.CASCADE,
        related_name="images",
    )
    url = models.TextField()
    ordre = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "annonce_images"
        indexes = [models.Index(fields=["annonce"], name="idx_annonce_images_annonce")]
        ordering = ("ordre", "id")
