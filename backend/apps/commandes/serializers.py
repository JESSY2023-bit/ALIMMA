"""Sérialiseurs du panier Redis."""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer

from apps.catalogue.serializers import AnnonceSerializer


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
