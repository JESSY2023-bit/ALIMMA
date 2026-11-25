"""Sérialiseurs d'administration."""
from rest_framework import serializers

from apps.accounts.models import Utilisateur


class UtilisateurAdministrationSerializer(serializers.ModelSerializer):
    """Expose les informations nécessaires à la supervision des comptes."""

    class Meta:
        model = Utilisateur
        fields = (
            "id",
            "nom",
            "email",
            "telephone",
            "role",
            "est_actif",
            "date_inscription",
        )
        read_only_fields = fields


class ChangementRoleSerializer(serializers.Serializer):
    """Valide strictement une valeur de l'enum PostgreSQL ``role_utilisateur``."""

    role = serializers.ChoiceField(choices=Utilisateur.Role.values)
