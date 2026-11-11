"""Vues de validation humaine des annonces publiées sur ALIMMA."""
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import ErreurSerializer
from apps.administration.models import JournalModeration
from apps.catalogue.models import Annonce
from apps.catalogue.serializers import AnnonceSerializer
from apps.catalogue.views import invalider_cache_annonces_publiques

from .permissions import EstModerateurOuAdmin
from .serializers import DecisionModerationSerializer
from .services import NotificationService


class ConflitModeration(APIException):
    """Empêche qu'une annonce déjà traitée reçoive une seconde décision."""

    status_code = status.HTTP_409_CONFLICT
    default_code = "CONFLICT"
    default_detail = "Cette annonce a déjà été traitée."


class AnnoncesModerationView(APIView):
    """Expose la file chronologique destinée aux modérateurs autorisés."""

    permission_classes = [IsAuthenticated, EstModerateurOuAdmin]
    serializer_class = AnnonceSerializer

    @extend_schema(
        tags=["Modération"],
        responses={
            200: AnnonceSerializer(many=True),
            401: ErreurSerializer,
            403: ErreurSerializer,
        },
        operation_id="moderation_annonces_list",
        summary="Lister les annonces en attente de modération",
    )
    def get(self, request):
        """Retourne la plus ancienne annonce en attente en premier."""
        annonces = (
            Annonce.objects.filter(statut=Annonce.Statut.EN_ATTENTE_MODERATION)
            .select_related("vendeur", "categorie")
            .prefetch_related("images")
            .order_by("created_at", "id")
        )
        return Response(AnnonceSerializer(annonces, many=True).data)


class DecisionAnnonceModerationView(APIView):
    """Applique de manière atomique une validation ou un rejet d'annonce."""

    permission_classes = [IsAuthenticated, EstModerateurOuAdmin]
    serializer_class = DecisionModerationSerializer

    @extend_schema(
        tags=["Modération"],
        request=DecisionModerationSerializer,
        responses={
            200: AnnonceSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            409: ErreurSerializer,
            422: ErreurSerializer,
        },
        operation_id="moderation_annonces_decision_create",
        summary="Valider ou rejeter une annonce",
    )
    def post(self, request, id):
        """Mémorise la décision, son motif, son audit et notifie le vendeur."""
        serializer = DecisionModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = serializer.validated_data["decision"]
        motif = serializer.validated_data["motif"]

        with transaction.atomic():
            try:
                annonce = (
                    Annonce.objects.select_for_update()
                    .select_related("vendeur", "categorie")
                    .prefetch_related("images")
                    .get(pk=id)
                )
            except Annonce.DoesNotExist as exc:
                raise NotFound("Annonce introuvable.") from exc
            if annonce.statut != Annonce.Statut.EN_ATTENTE_MODERATION:
                raise ConflitModeration()

            if decision == "valider":
                annonce.statut = Annonce.Statut.ACTIVE
                annonce.date_publication = timezone.now()
                action = "annonce_validee"
            else:
                annonce.statut = Annonce.Statut.REJETEE
                action = "annonce_rejetee"
            annonce.save(update_fields=["statut", "date_publication", "updated_at"])
            JournalModeration.objects.create(
                moderateur=request.user,
                action=action,
                cible_type="annonce",
                cible_id=annonce.id,
                details=motif or None,
            )

        invalider_cache_annonces_publiques()
        NotificationService.notifier_decision_annonce(
            vendeur=annonce.vendeur,
            annonce=annonce,
            decision=decision,
            motif=motif,
        )
        return Response(AnnonceSerializer(annonce).data)
