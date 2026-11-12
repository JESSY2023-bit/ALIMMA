"""Vues authentifiées de gestion du panier Redis."""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import ErreurSerializer
from apps.catalogue.models import Annonce

from .serializers import (
    PanierArticleEcritureSerializer,
    PanierQuantiteSerializer,
    PanierSerializer,
)
from .services import construire_panier, enregistrer_contenu, lire_contenu


def reponse_panier(utilisateur_id):
    """Sérialise le panier recalculé avant de le remettre au renderer JSON."""
    panier = construire_panier(utilisateur_id)
    return Response(PanierSerializer(panier).data)


class PanierView(APIView):
    """Lit ou vide le panier du compte authentifié."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Panier & Commandes"],
        responses={200: PanierSerializer, 401: ErreurSerializer},
        operation_id="panier_retrieve",
        summary="Consulter mon panier",
    )
    def get(self, request):
        """Retourne les montants recalculés depuis les annonces actives."""
        return reponse_panier(request.user.id)

    @extend_schema(
        tags=["Panier & Commandes"],
        responses={204: None, 401: ErreurSerializer},
        operation_id="panier_destroy",
        summary="Vider mon panier",
    )
    def delete(self, request):
        """Supprime uniquement la clé Redis du panier authentifié."""
        enregistrer_contenu(request.user.id, {})
        return Response(status=status.HTTP_204_NO_CONTENT)


class PanierArticlesView(APIView):
    """Ajoute une annonce active au panier du compte authentifié."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Panier & Commandes"],
        request=PanierArticleEcritureSerializer,
        responses={
            200: PanierSerializer,
            401: ErreurSerializer,
            404: ErreurSerializer,
            422: ErreurSerializer,
        },
        operation_id="panier_articles_create",
        summary="Ajouter un article au panier",
    )
    def post(self, request):
        """Ajoute ou cumule la quantité sans accepter un prix provenant du client."""
        serializer = PanierArticleEcritureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        annonce_id = serializer.validated_data["annonce_id"]
        try:
            annonce = Annonce.objects.get(pk=annonce_id, statut=Annonce.Statut.ACTIVE)
        except Annonce.DoesNotExist as exc:
            raise NotFound("Annonce active introuvable.") from exc
        if annonce.vendeur_id == request.user.id:
            raise ValidationError("Vous ne pouvez pas ajouter votre propre annonce au panier.")
        contenu = lire_contenu(request.user.id)
        cle = str(annonce_id)
        contenu[cle] = contenu.get(cle, 0) + serializer.validated_data["quantite"]
        enregistrer_contenu(request.user.id, contenu)
        return reponse_panier(request.user.id)


class PanierArticleDetailView(APIView):
    """Modifie ou retire une ligne de panier identifiée par son annonce."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Panier & Commandes"],
        request=PanierQuantiteSerializer,
        responses={
            200: PanierSerializer,
            401: ErreurSerializer,
            404: ErreurSerializer,
            422: ErreurSerializer,
        },
        operation_id="panier_articles_partial_update",
        summary="Modifier la quantité d'un article",
    )
    def patch(self, request, annonce_id):
        """Remplace la quantité d'une ligne existante par une valeur strictement positive."""
        serializer = PanierQuantiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contenu = lire_contenu(request.user.id)
        cle = str(annonce_id)
        if cle not in contenu:
            raise NotFound("Cet article n'est pas dans votre panier.")
        contenu[cle] = serializer.validated_data["quantite"]
        enregistrer_contenu(request.user.id, contenu)
        return reponse_panier(request.user.id)

    @extend_schema(
        tags=["Panier & Commandes"],
        responses={204: None, 401: ErreurSerializer, 404: ErreurSerializer},
        operation_id="panier_articles_destroy",
        summary="Retirer un article du panier",
    )
    def delete(self, request, annonce_id):
        """Retire une seule ligne sans toucher aux autres articles Redis."""
        contenu = lire_contenu(request.user.id)
        try:
            del contenu[str(annonce_id)]
        except KeyError as exc:
            raise NotFound("Cet article n'est pas dans votre panier.") from exc
        enregistrer_contenu(request.user.id, contenu)
        return Response(status=status.HTTP_204_NO_CONTENT)
