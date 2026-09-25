"""Vues d'authentification des utilisateurs ALIMMA."""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ErreurSerializer,
    InscriptionSerializer,
    UtilisateurSerializer,
)


class InscriptionView(APIView):
    """Crée un compte utilisateur depuis les données d'inscription publiques."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        auth=[],
        request=InscriptionSerializer,
        responses={201: UtilisateurSerializer, 422: ErreurSerializer},
        summary="Créer un compte utilisateur",
    )
    def post(self, request):
        serializer = InscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        utilisateur = serializer.save()
        return Response(
            UtilisateurSerializer(utilisateur).data,
            status=status.HTTP_201_CREATED,
        )
