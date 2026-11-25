"""Sérialiseurs du panier Redis."""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer

from apps.catalogue.serializers import AnnonceSerializer
from apps.accounts.utils import TELEPHONE_ERROR_MESSAGE, normaliser_telephone

from .models import Commande, HistoriqueStatutCommande


@extend_schema_serializer(component_name="PanierArticleRequest")
class PanierArticleEcritureSerializer(serializers.Serializer):
    """Valide l'identifiant et la quantité d'une ligne de panier."""

    annonce_id = serializers.IntegerField(min_value=1)
    quantite = serializers.IntegerField(min_value=1)


@extend_schema_serializer(component_name="PanierQuantiteRequest")
class PanierQuantiteSerializer(serializers.Serializer):
    """Valide la quantité d'une ligne déjà présente dans le panier."""

    quantite = serializers.IntegerField(min_value=1)


@extend_schema_serializer(component_name="PanierArticle")
class PanierArticleSerializer(serializers.Serializer):
    """Expose une ligne recalculée depuis l'annonce actuellement active."""

    annonce = AnnonceSerializer(read_only=True)
    quantite = serializers.IntegerField(read_only=True)
    prix_unitaire = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, coerce_to_string=False
    )
    total_ligne = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, coerce_to_string=False
    )


@extend_schema_serializer(component_name="Panier")
class PanierSerializer(serializers.Serializer):
    """Représentation complète du panier et de ses montants recalculés."""

    articles = PanierArticleSerializer(many=True, read_only=True)
    sous_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, coerce_to_string=False
    )
    frais_livraison = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, coerce_to_string=False
    )
    total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, coerce_to_string=False
    )
    message = serializers.CharField(read_only=True, required=False)


@extend_schema_serializer(component_name="CommandeCreateRequest")
class CommandeCreationSerializer(serializers.Serializer):
    """Valide le corps de création d'une commande individuelle."""

    annonce_id = serializers.IntegerField(min_value=1)
    mode_paiement = serializers.ChoiceField(choices=Commande.ModePaiement.choices)
    operateur = serializers.ChoiceField(
        choices=("mtn", "orange"), required=False, allow_null=True
    )
    mode_remise = serializers.ChoiceField(choices=Commande.ModeRemise.choices)
    ville = serializers.CharField(max_length=100, allow_blank=False)
    quartier = serializers.CharField(max_length=100, allow_blank=False)
    repere = serializers.CharField(max_length=200, allow_blank=False)
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, required=False, allow_null=True
    )
    telephone_contact = serializers.CharField(max_length=20)
    code_promo = serializers.CharField(max_length=30, required=False, allow_blank=False)

    def validate_telephone_contact(self, value):
        """Réutilise la normalisation E.164 camerounaise des comptes."""
        try:
            return normaliser_telephone(value)
        except ValueError as exc:
            raise serializers.ValidationError(TELEPHONE_ERROR_MESSAGE) from exc

    def validate(self, attrs):
        """Évite une coordonnée isolée et rejette l'ancienne quantité métier."""
        if "quantite" in self.initial_data:
            raise serializers.ValidationError(
                {"quantite": "Une annonce est unique : ce champ n'est pas accepté."}
            )
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")
        if (latitude is None) != (longitude is None):
            raise serializers.ValidationError(
                {"localisation": "Latitude et longitude doivent être fournies ensemble."}
            )
        return attrs


@extend_schema_serializer(component_name="Commande")
class CommandeSerializer(serializers.ModelSerializer):
    """Représentation publique d'une commande créée ou consultée."""

    acheteur_id = serializers.IntegerField(read_only=True)
    annonce_id = serializers.IntegerField(read_only=True)
    vendeur_id = serializers.IntegerField(read_only=True)
    montant_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, coerce_to_string=False
    )
    message = serializers.CharField(read_only=True, required=False)
    historique = serializers.SerializerMethodField()

    def get_historique(self, commande):
        """Expose la trace d'état ordonnée dans le détail de commande."""
        historique = getattr(commande, "historique_statuts", None)
        elements = historique.all() if historique is not None else []
        return HistoriqueStatutCommandeSerializer(elements, many=True).data

    class Meta:
        model = Commande
        fields = (
            "id",
            "acheteur_id",
            "annonce_id",
            "vendeur_id",
            "montant_total",
            "mode_paiement",
            "statut",
            "mode_remise",
            "ville",
            "quartier",
            "repere",
            "latitude",
            "longitude",
            "telephone_contact",
            "created_at",
            "historique",
            "message",
        )
        read_only_fields = fields


@extend_schema_serializer(component_name="HistoriqueStatutCommande")
class HistoriqueStatutCommandeSerializer(serializers.ModelSerializer):
    """Représentation de la transition effectuée par un acteur ou le système."""

    acteur_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = HistoriqueStatutCommande
        fields = (
            "id",
            "ancien_statut",
            "nouveau_statut",
            "acteur_id",
            "motif",
            "created_at",
        )
        read_only_fields = fields


class MotifCommandeSerializer(serializers.Serializer):
    """Valide le motif obligatoire lors du refus explicite du vendeur."""

    motif = serializers.CharField(max_length=500, allow_blank=False)
