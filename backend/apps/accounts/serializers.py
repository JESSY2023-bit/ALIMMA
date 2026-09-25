"""Sérialiseurs de l'inscription et du profil utilisateur."""
import re

from django.db import transaction
from rest_framework import serializers

from .models import Parrainage, Utilisateur

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


class ErreurSerializer(serializers.Serializer):
    """Format uniforme des erreurs défini dans le contrat OpenAPI."""

    code = serializers.CharField()
    message = serializers.CharField()


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
        with transaction.atomic():
            utilisateur = Utilisateur.objects.create_user(**validated_data)
            parrain = Utilisateur.objects.filter(
                code_parrainage=(code_utilise or "").strip().upper()
            ).first()
            if parrain:
                utilisateur.parraine_par = parrain
                utilisateur.save(update_fields=["parraine_par", "updated_at"])
                Parrainage.objects.create(parrain=parrain, filleul=utilisateur)
        return utilisateur
