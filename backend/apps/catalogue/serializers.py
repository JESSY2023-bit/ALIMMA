"""Sérialiseurs du catalogue."""
from django.utils.text import slugify
from rest_framework import serializers

from .models import Categorie


class CategorieEnfantSerializer(serializers.ModelSerializer):
    """Représentation plate d'une sous-catégorie dans l'arborescence."""

    parent_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Categorie
        fields = ("id", "nom", "slug", "parent_id", "icone_url", "ordre_affichage")
        read_only_fields = fields


class CategorieSerializer(serializers.ModelSerializer):
    """Représente une catégorie et ses sous-catégories directes."""

    enfants = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Categorie
        fields = ("id", "nom", "slug", "parent_id", "icone_url", "ordre_affichage", "enfants")
        read_only_fields = fields

    def get_enfants(self, instance):
        """Sérialise un unique niveau enfant, conformément à la règle métier."""
        enfants = instance.enfants.all().order_by("ordre_affichage", "nom", "id")
        return CategorieEnfantSerializer(enfants, many=True).data


class CategorieEcritureSerializer(serializers.ModelSerializer):
    """Valide une catégorie sans laisser le client imposer son slug."""

    parent_id = serializers.PrimaryKeyRelatedField(
        source="parent",
        queryset=Categorie.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Categorie
        fields = ("nom", "parent_id", "icone_url", "ordre_affichage")
        extra_kwargs = {
            "icone_url": {"required": False, "allow_null": True, "allow_blank": True},
            "ordre_affichage": {"required": False},
        }

    def validate_parent_id(self, parent):
        """Interdit les cycles et une profondeur supérieure à parent → enfant."""
        instance = self.instance
        if instance and parent and parent.pk == instance.pk:
            raise serializers.ValidationError("Une catégorie ne peut pas être son propre parent.")
        if parent and parent.parent_id is not None:
            raise serializers.ValidationError(
                "La profondeur maximale est catégorie puis sous-catégorie."
            )
        return parent

    @staticmethod
    def _slug_unique(nom, instance=None):
        """Construit un slug lisible, suffixé en cas de collision en base."""
        base_slug = slugify(nom) or "categorie"
        max_length = Categorie._meta.get_field("slug").max_length
        candidat = base_slug[:max_length]
        index = 2
        queryset = Categorie.objects.all()
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        while queryset.filter(slug=candidat).exists():
            suffixe = f"-{index}"
            candidat = f"{base_slug[:max_length - len(suffixe)]}{suffixe}"
            index += 1
        return candidat

    def create(self, validated_data):
        """Ajoute le slug généré côté serveur à la création."""
        validated_data["slug"] = self._slug_unique(validated_data["nom"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Régénère le slug si le nom est modifié par un administrateur."""
        nom = validated_data.get("nom")
        if nom and nom != instance.nom:
            validated_data["slug"] = self._slug_unique(nom, instance)
        return super().update(instance, validated_data)
