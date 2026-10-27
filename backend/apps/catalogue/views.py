"""Vues du catalogue."""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import EstAdministrateur
from apps.accounts.serializers import ErreurSerializer

from .models import Annonce, Categorie
from .serializers import CategorieEcritureSerializer, CategorieSerializer


class ConflitCategorie(APIException):
    """Signale une suppression impossible sans la transformer en erreur serveur."""

    status_code = status.HTTP_409_CONFLICT
    default_code = "CONFLICT"
    default_detail = "La catégorie ne peut pas être supprimée."


class CategoriesAdministrationView(APIView):
    """Expose l'arborescence publiquement et limite sa création aux administrateurs."""

    def get_permissions(self):
        """Déclare une permission explicite pour chaque méthode de la route."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), EstAdministrateur()]

    @extend_schema(
        tags=["Administration"],
        auth=[],
        responses={200: CategorieSerializer(many=True)},
        summary="Lister les catégories et sous-catégories",
    )
    def get(self, request):
        """Retourne les seules racines avec leurs enfants directs préchargés."""
        categories = Categorie.objects.filter(parent__isnull=True).prefetch_related("enfants")
        categories = categories.order_by("ordre_affichage", "nom", "id")
        return Response(CategorieSerializer(categories, many=True).data)

    @extend_schema(
        tags=["Administration"],
        request=CategorieEcritureSerializer,
        responses={
            201: CategorieSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            422: ErreurSerializer,
        },
        summary="Créer une catégorie ou sous-catégorie",
    )
    def post(self, request):
        """Crée une racine ou une sous-catégorie dans la profondeur autorisée."""
        serializer = CategorieEcritureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categorie = serializer.save()
        return Response(CategorieSerializer(categorie).data, status=status.HTTP_201_CREATED)


class CategorieAdministrationDetailView(APIView):
    """Modifie ou supprime une catégorie pour le seul rôle administrateur."""

    permission_classes = [IsAuthenticated, EstAdministrateur]

    @staticmethod
    def get_categorie(id):
        """Retourne la catégorie demandée avec une erreur API normalisée si absente."""
        try:
            return Categorie.objects.get(pk=id)
        except Categorie.DoesNotExist as exc:
            raise NotFound("Catégorie introuvable.") from exc

    @extend_schema(
        tags=["Administration"],
        request=CategorieEcritureSerializer,
        responses={
            200: CategorieSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            422: ErreurSerializer,
        },
        summary="Modifier une catégorie",
    )
    def patch(self, request, id):
        """Met à jour une catégorie, son parent et son slug généré si requis."""
        categorie = self.get_categorie(id)
        serializer = CategorieEcritureSerializer(categorie, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        categorie = serializer.save()
        return Response(CategorieSerializer(categorie).data)

    @extend_schema(
        tags=["Administration"],
        responses={
            204: None,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            409: ErreurSerializer,
        },
        summary="Supprimer une catégorie vide",
    )
    def delete(self, request, id):
        """Supprime seulement une catégorie sans enfant ni annonce rattachée."""
        categorie = self.get_categorie(id)
        if categorie.enfants.exists():
            raise ConflitCategorie("Cette catégorie possède des sous-catégories.")
        if Annonce.objects.filter(categorie=categorie).exists():
            raise ConflitCategorie("Cette catégorie possède des annonces rattachées.")
        categorie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
