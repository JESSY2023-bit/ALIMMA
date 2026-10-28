"""Sérialiseurs du catalogue."""
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.text import slugify
from rest_framework import serializers

from .models import Annonce, AnnonceImage, Categorie


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


class AnnonceImageSerializer(serializers.ModelSerializer):
    """Expose les URL des images dans l'ordre de publication choisi."""

    class Meta:
        model = AnnonceImage
        fields = ("url", "ordre")
        read_only_fields = fields


class AnnonceSerializer(serializers.ModelSerializer):
    """Représentation API d'une annonce, sans exposer de données du vendeur."""

    vendeur_id = serializers.IntegerField(read_only=True)
    categorie_id = serializers.IntegerField(read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Annonce
        fields = (
            "id",
            "vendeur_id",
            "categorie_id",
            "titre",
            "description",
            "prix",
            "type_vente",
            "etat",
            "ville",
            "quartier",
            "latitude",
            "longitude",
            "statut",
            "nb_vues",
            "date_publication",
            "date_expiration",
            "images",
        )
        read_only_fields = fields

    def get_images(self, instance):
        """Conserve l'ordre défini lors de l'upload multipart."""
        return [image.url for image in instance.images.all()]


class AnnonceCreationSerializer(serializers.ModelSerializer):
    """Valide une publication multipart et force ses attributs sensibles côté serveur."""

    categorie_id = serializers.PrimaryKeyRelatedField(
        source="categorie",
        queryset=Categorie.objects.all(),
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        min_length=1,
        max_length=8,
        write_only=True,
    )

    class Meta:
        model = Annonce
        fields = (
            "titre",
            "description",
            "prix",
            "categorie_id",
            "ville",
            "quartier",
            "latitude",
            "longitude",
            "etat",
            "type_vente",
            "images",
        )
        extra_kwargs = {
            "quartier": {"required": False, "allow_null": True, "allow_blank": True},
            "latitude": {"required": False, "allow_null": True},
            "longitude": {"required": False, "allow_null": True},
            "prix": {"min_value": Decimal("0")},
        }

    def validate_images(self, images):
        """Vérifie la limite unitaire et les formats réellement autorisés."""
        for image in images:
            if image.size > settings.ANNONCE_IMAGE_MAX_SIZE:
                raise serializers.ValidationError(
                    "Chaque image ne doit pas dépasser 5 Mo."
                )
            if image.content_type not in settings.ANNONCE_IMAGE_ALLOWED_MIME_TYPES:
                raise serializers.ValidationError("Le format doit être JPEG, PNG ou WebP.")
        return images

    def validate(self, attrs):
        """Exige une paire de coordonnées complète et dans les bornes terrestres."""
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")
        if (latitude is None) != (longitude is None):
            raise serializers.ValidationError(
                "Latitude et longitude doivent être fournies ensemble."
            )
        if latitude is not None and not -90 <= latitude <= 90:
            raise serializers.ValidationError(
                {"latitude": "La latitude doit être entre -90 et 90."}
            )
        if longitude is not None and not -180 <= longitude <= 180:
            raise serializers.ValidationError(
                {"longitude": "La longitude doit être entre -180 et 180."}
            )
        return attrs

    def create(self, validated_data):
        """Crée l'annonce en attente puis stocke ses images dans l'ordre reçu."""
        images = validated_data.pop("images")
        vendeur = self.context["vendeur"]
        latitude = validated_data.get("latitude")
        longitude = validated_data.get("longitude")
        if latitude is not None:
            # Le standard WKT place longitude avant latitude ; PostGIS convertit
            # cette valeur dans la colonne GEOGRAPHY(POINT,4326).
            validated_data["localisation"] = (
                f"SRID=4326;POINT({longitude} {latitude})"
            )
        annonce = Annonce.objects.create(
            vendeur=vendeur,
            statut=Annonce.Statut.EN_ATTENTE_MODERATION,
            **validated_data,
        )
        for ordre, image in enumerate(images):
            extension = image.name.rsplit(".", 1)[-1].lower() if "." in image.name else ""
            filename = f"annonces/{annonce.id}/{uuid4().hex}{'.' + extension if extension else ''}"
            chemin = default_storage.save(filename, image)
            AnnonceImage.objects.create(
                annonce=annonce,
                url=default_storage.url(chemin),
                ordre=ordre,
            )
        return annonce
