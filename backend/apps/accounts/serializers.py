"""Sérialiseurs de l'inscription et du profil utilisateur."""
import re
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers

from .models import Parrainage, Utilisateur

# Le format E.164 camerounais contient l'indicatif +237 suivi de neuf chiffres.
CAMEROON_PHONE_PATTERN = re.compile(r"^\+237\d{9}$")


class UtilisateurSerializer(serializers.ModelSerializer):
    """Représentation publique strictement limitée au contrat OpenAPI."""

    class Meta:
        model = Utilisateur
        fields = (
            "id",
            "nom",
            "email",
            "telephone",
            "role",
            "photo_url",
            "note_moyenne",
            "code_parrainage",
            "date_inscription",
        )
        read_only_fields = fields


class ProfilUtilisateurSerializer(serializers.ModelSerializer):
    """Représentation complète du compte réservée à son propriétaire."""

    class Meta:
        model = Utilisateur
        fields = (
            "id",
            "nom",
            "email",
            "telephone",
            "role",
            "photo_url",
            "note_moyenne",
            "nb_avis",
            "points_parrainage",
            "code_parrainage",
            "deux_fa_active",
            "derniere_connexion",
            "date_inscription",
        )
        read_only_fields = fields


class ProfilPublicSerializer(serializers.ModelSerializer):
    """Représentation non sensible d'un vendeur visible par tous les visiteurs."""

    class Meta:
        model = Utilisateur
        fields = (
            "id",
            "nom",
            "photo_url",
            "note_moyenne",
            "nb_avis",
            "date_inscription",
        )
        read_only_fields = fields


class ProfilUpdateSerializer(serializers.ModelSerializer):
    """Valide les seuls attributs modifiables du profil personnel."""

    photo = serializers.FileField(required=False, write_only=True)

    class Meta:
        model = Utilisateur
        fields = ("nom", "email", "photo_url", "photo")
        extra_kwargs = {
            "nom": {"required": False},
            "email": {"required": False, "allow_null": True, "allow_blank": True},
            "photo_url": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def validate_email(self, value):
        """Garantit l'unicité de l'e-mail hors du compte en cours de modification."""
        if value in (None, ""):
            return None
        email = value.strip().lower()
        if Utilisateur.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise serializers.ValidationError("Cet e-mail est déjà utilisé.")
        return email

    def validate_photo(self, value):
        """Vérifie la taille, le MIME déclaré et le véritable format de l'image."""
        if value.size > settings.PROFILE_PHOTO_MAX_SIZE:
            raise serializers.ValidationError("La photo de profil ne doit pas dépasser 2 Mo.")
        if value.content_type not in settings.PROFILE_PHOTO_ALLOWED_MIME_TYPES:
            raise serializers.ValidationError("Le format de photo doit être JPEG, PNG ou WebP.")
        try:
            # ``verify`` force Pillow à valider les données et non le seul nom
            # du fichier ou l'en-tête MIME fourni par le client.
            image = Image.open(value)
            image_format = image.format
            image.verify()
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError) as exc:
            raise serializers.ValidationError("Le fichier fourni n'est pas une image valide.") from exc
        finally:
            # Le stockage Django doit relire le fichier depuis le début après
            # l'inspection réalisée par Pillow.
            value.seek(0)
        if image_format not in {"JPEG", "PNG", "WEBP"}:
            raise serializers.ValidationError("Le format de photo doit être JPEG, PNG ou WebP.")
        return value

    def update(self, instance, validated_data):
        """Enregistre le fichier via le stockage configuré avant de mettre à jour le profil."""
        photo = validated_data.pop("photo", None)
        if photo is not None:
            # Un nom opaque évite les collisions et ne révèle pas le nom local
            # du fichier transmis par l'utilisateur.
            extension = photo.name.rsplit(".", 1)[-1].lower() if "." in photo.name else ""
            filename = f"profils/{uuid4().hex}{'.' + extension if extension else ''}"
            saved_path = default_storage.save(filename, photo)
            validated_data["photo_url"] = default_storage.url(saved_path)
        return super().update(instance, validated_data)


class ProfilUpdateJsonSerializer(serializers.Serializer):
    """Documente la variante JSON, limitée aux trois champs textuels autorisés."""

    nom = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)


class ChangementMotDePasseSerializer(serializers.Serializer):
    """Valide les deux secrets nécessaires au changement de mot de passe."""

    ancien_mot_de_passe = serializers.CharField(write_only=True, trim_whitespace=False)
    nouveau_mot_de_passe = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )


class ErreurSerializer(serializers.Serializer):
    """Format uniforme des erreurs défini dans le contrat OpenAPI."""

    code = serializers.CharField()
    message = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    """Valide les identifiants attendus par l'endpoint de connexion."""

    identifiant = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class RefreshRequestSerializer(serializers.Serializer):
    """Valide le refresh token transmis par le client."""

    refresh_token = serializers.CharField()


class LogoutSerializer(RefreshRequestSerializer):
    """Le logout nécessite le même refresh token que son invalidation."""


class LoginResponseSerializer(serializers.Serializer):
    """Documente les réponses de connexion avec ou sans authentification 2FA."""

    otp_requis = serializers.BooleanField()
    message = serializers.CharField(required=False)
    session_token = serializers.CharField(required=False)
    access_token = serializers.CharField(required=False)
    refresh_token = serializers.CharField(required=False)
    utilisateur = UtilisateurSerializer(required=False)


class InscriptionSerializer(serializers.Serializer):
    """Valide et crée une inscription depuis ``InscriptionRequest``."""

    nom = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_null=True)
    telephone = serializers.CharField(max_length=20)
    password = serializers.CharField(
        write_only=True, min_length=8, trim_whitespace=False
    )
    code_parrainage_utilise = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    def validate_telephone(self, value):
        """Normalise un numéro local en E.164 et limite le pays au Cameroun."""
        telephone = value.strip().replace(" ", "").replace("-", "")
        if telephone.isdigit() and len(telephone) == 9:
            telephone = f"+237{telephone}"
        if not CAMEROON_PHONE_PATTERN.fullmatch(telephone):
            raise serializers.ValidationError(
                "Le téléphone doit être au format +237XXXXXXXXX."
            )
        if Utilisateur.objects.filter(telephone=telephone).exists():
            raise serializers.ValidationError("Ce téléphone est déjà utilisé.")
        return telephone

    def validate_email(self, value):
        """Empêche l'inscription avec une adresse e-mail déjà enregistrée."""
        if value in (None, ""):
            return None
        email = value.strip().lower()
        if Utilisateur.objects.filter(email=email).exists():
            raise serializers.ValidationError("Cet e-mail est déjà utilisé.")
        return email

    def create(self, validated_data):
        """Crée le compte et applique un parrainage valide, sans bloquer sinon."""
        code_utilise = validated_data.pop("code_parrainage_utilise", "")
        # La transaction garantit qu'un filleul ne peut pas être créé sans son
        # lien de parrainage lorsque le code fourni est valide.
        with transaction.atomic():
            utilisateur = Utilisateur.objects.create_user(**validated_data)
            parrain = Utilisateur.objects.filter(
                code_parrainage=(code_utilise or "").strip().upper()
            ).first()
            if parrain:
                # Un code absent ou inconnu est volontairement ignoré, selon le
                # comportement attendu à l'inscription.
                utilisateur.parraine_par = parrain
                utilisateur.save(update_fields=["parraine_par", "updated_at"])
                Parrainage.objects.create(parrain=parrain, filleul=utilisateur)
        return utilisateur
