"""Vues d'administration API."""
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.accounts.models import ProfilLivreur, ProfilVendeurPro, Utilisateur
from apps.accounts.permissions import EstAdministrateur
from apps.accounts.serializers import ErreurSerializer

from .models import JournalModeration
from .serializers import ChangementRoleSerializer, UtilisateurAdministrationSerializer


def journaliser_action(administrateur, action, cible, details=""):
    """Conserve une trace exploitable de toute action administrative sensible."""
    JournalModeration.objects.create(
        moderateur=administrateur,
        action=action,
        cible_type="utilisateur",
        cible_id=cible.id,
        details=details,
    )


def invalider_refresh_tokens(utilisateur):
    """Blackliste tous les refresh tokens émis pour un compte suspendu."""
    for token in OutstandingToken.objects.filter(user=utilisateur):
        BlacklistedToken.objects.get_or_create(token=token)


class UtilisateursAdministrationView(APIView):
    """Liste les comptes avec filtre de rôle et recherche multi-champs."""

    permission_classes = [IsAuthenticated, EstAdministrateur]

    @extend_schema(
        tags=["Administration"],
        parameters=[
            OpenApiParameter("role", str, OpenApiParameter.QUERY),
            OpenApiParameter("q", str, OpenApiParameter.QUERY),
        ],
        responses={
            200: UtilisateurAdministrationSerializer(many=True),
            401: ErreurSerializer,
            403: ErreurSerializer,
        },
        summary="Lister ou rechercher les utilisateurs",
    )
    def get(self, request):
        """Retourne une page stable de comptes filtrés sans exposer leur hash."""
        utilisateurs = Utilisateur.objects.all().order_by("id")
        role = request.query_params.get("role")
        recherche = request.query_params.get("q", "").strip()
        if role:
            utilisateurs = utilisateurs.filter(role=role)
        if recherche:
            utilisateurs = utilisateurs.filter(
                Q(nom__icontains=recherche)
                | Q(email__icontains=recherche)
                | Q(telephone__icontains=recherche)
            )
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(utilisateurs, request, view=self)
        return paginator.get_paginated_response(
            UtilisateurAdministrationSerializer(page, many=True).data
        )


class SuspensionUtilisateurView(APIView):
    """Bascule le statut d'un compte sans permettre l'auto-suspension."""

    permission_classes = [IsAuthenticated, EstAdministrateur]

    @extend_schema(
        tags=["Administration"],
        responses={
            200: UtilisateurAdministrationSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
        },
        summary="Suspendre ou réactiver un compte utilisateur",
    )
    def post(self, request, id):
        """Inverse ``est_actif``, blackliste les refresh et journalise l'action."""
        with transaction.atomic():
            try:
                utilisateur = Utilisateur.objects.select_for_update().get(pk=id)
            except Utilisateur.DoesNotExist as exc:
                raise NotFound("Utilisateur introuvable.") from exc
            if utilisateur.id == request.user.id:
                raise PermissionDenied("Un administrateur ne peut pas se suspendre lui-même.")
            utilisateur.est_actif = not utilisateur.est_actif
            utilisateur.save(update_fields=["est_actif", "updated_at"])
            if not utilisateur.est_actif:
                invalider_refresh_tokens(utilisateur)
                action = "utilisateur_suspendu"
            else:
                action = "utilisateur_reactive"
            journaliser_action(request.user, action, utilisateur)
        return Response(
            UtilisateurAdministrationSerializer(utilisateur).data,
            status=status.HTTP_200_OK,
        )


class RoleUtilisateurView(APIView):
    """Modifie le rôle et initialise le profil métier correspondant si nécessaire."""

    permission_classes = [IsAuthenticated, EstAdministrateur]

    @extend_schema(
        tags=["Administration"],
        request=ChangementRoleSerializer,
        responses={
            200: UtilisateurAdministrationSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            422: ErreurSerializer,
        },
        summary="Modifier le rôle d'un utilisateur",
    )
    def patch(self, request, id):
        """Persiste le rôle et garde les anciens profils pour préserver l'historique."""
        serializer = ChangementRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nouveau_role = serializer.validated_data["role"]
        with transaction.atomic():
            try:
                utilisateur = Utilisateur.objects.select_for_update().get(pk=id)
            except Utilisateur.DoesNotExist as exc:
                raise NotFound("Utilisateur introuvable.") from exc
            ancien_role = utilisateur.role
            utilisateur.role = nouveau_role
            utilisateur.save(update_fields=["role", "updated_at"])
            if nouveau_role == Utilisateur.Role.VENDEUR_PRO:
                ProfilVendeurPro.objects.get_or_create(
                    utilisateur=utilisateur,
                    defaults={"nom_boutique": utilisateur.nom},
                )
            elif nouveau_role == Utilisateur.Role.LIVREUR:
                ProfilLivreur.objects.get_or_create(utilisateur=utilisateur)
            journaliser_action(
                request.user,
                "utilisateur_role_modifie",
                utilisateur,
                details=f"ancien_role={ancien_role}; nouveau_role={nouveau_role}",
            )
        return Response(UtilisateurAdministrationSerializer(utilisateur).data)
