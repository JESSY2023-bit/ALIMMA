"""Sérialiseurs de modération."""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer


@extend_schema_serializer(component_name="DecisionModerationRequest")
class DecisionModerationSerializer(serializers.Serializer):
    """Valide la décision humaine appliquée à une annonce en attente."""

    decision = serializers.ChoiceField(choices=("valider", "rejeter"))
    motif = serializers.CharField(required=False, allow_blank=True, max_length=2000)

    def validate(self, attrs):
        """Exige une explication exploitable lorsque le vendeur est rejeté."""
        motif = attrs.get("motif", "").strip()
        if attrs["decision"] == "rejeter" and not motif:
            raise serializers.ValidationError(
                {"motif": "Le motif est obligatoire lors d'un rejet."}
            )
        attrs["motif"] = motif
        return attrs
