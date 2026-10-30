"""Vues d'authentification des utilisateurs ALIMMA."""
from django.conf import settings
from django.core import signing
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ErreurSerializer,
    ChangementMotDePasseSerializer,
    InscriptionSerializer,
    LoginSerializer,
    LogoutSerializer,
    RefreshRequestSerializer,
    LoginResponseSerializer,
    ProfilPublicSerializer,
    ProfilUpdateJsonSerializer,
    ProfilUpdateSerializer,
    ProfilUtilisateurSerializer,
    UtilisateurSerializer,
)
from .models import Utilisateur
from .services import LoginAttemptLimiter
from apps.catalogue.models import Annonce

INVALID_CREDENTIALS_MESSAGE = "Identifiants invalides."


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


def token_response(utilisateur, refresh_token=None):
    """Émet des JWT contenant les claims métier exigés par le contrat ALIMMA."""
    # Un refresh transmis n'est utilisé que pour construire son access token
    # associé. La vue de refresh crée toujours une nouvelle paire JWT.
    refresh = refresh_token or RefreshToken.for_user(utilisateur)
    # Ces claims évitent au client de devoir décoder des informations métier
    # absentes du payload standard de Simple JWT.
    for claim, value in {
        "id": utilisateur.id,
        "role": utilisateur.role,
        "telephone": utilisateur.telephone,
    }.items():
        refresh[claim] = value
    access = refresh.access_token
    return {
        "otp_requis": False,
        "access_token": str(access),
        "refresh_token": str(refresh),
        "utilisateur": UtilisateurSerializer(utilisateur).data,
    }


def active_user_from_refresh(refresh_token):
    """Valide un refresh token et retourne uniquement son propriétaire actif."""
    try:
        # Le constructeur contrôle signature, expiration et blacklist avant
        # toute lecture du claim ``user_id``.
        refresh = RefreshToken(refresh_token)
        utilisateur = Utilisateur.objects.get(
            id=refresh["user_id"],
            est_actif=True,
        )
    except (KeyError, TokenError, Utilisateur.DoesNotExist) as exc:
        raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE) from exc
    return refresh, utilisateur


class LoginView(APIView):
    """Authentifie par téléphone ou e-mail et émet une paire JWT."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        auth=[],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description="Paire JWT émise lorsque la 2FA est désactivée.",
                examples=[
                    OpenApiExample(
                        "Connexion réussie",
                        value={
                            "otp_requis": False,
                            "access_token": "<access_token>",
                            "refresh_token": "<refresh_token>",
                            "utilisateur": {"id": 1, "nom": "Alice Ngono"},
                        },
                        response_only=True,
                    )
                ],
            ),
            401: ErreurSerializer,
            422: ErreurSerializer,
        },
        examples=[
            OpenApiExample(
                "Connexion par e-mail",
                value={"identifiant": "alice@example.cm", "password": "mot-de-passe-solide"},
                request_only=True,
            )
        ],
        summary="Connexion",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["identifiant"]
        if LoginAttemptLimiter.is_blocked(identifier):
            raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

        utilisateur = Utilisateur.objects.filter(telephone=identifier).first()
        if utilisateur is None:
            utilisateur = Utilisateur.objects.filter(email__iexact=identifier).first()
        if (
            utilisateur is None
            or not utilisateur.est_actif
            or not utilisateur.check_password(serializer.validated_data["password"])
        ):
            # Le message reste volontairement générique pour ne pas révéler
            # l'existence d'un compte ni l'origine exacte de l'échec.
            LoginAttemptLimiter.register_failure(identifier)
            raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

        LoginAttemptLimiter.clear(identifier)
        utilisateur.derniere_connexion = timezone.now()
        utilisateur.save(update_fields=["derniere_connexion", "updated_at"])
        if settings.FEATURE_2FA_ENABLED and utilisateur.deux_fa_active:
            # La branche est prête pour l'OTP mais reste inactive pour le MVP.
            session_token = signing.TimestampSigner().sign(str(utilisateur.id))
            return Response(
                {
                    "otp_requis": True,
                    "message": "Code OTP envoyé par SMS",
                    "session_token": session_token,
                }
            )
        return Response(token_response(utilisateur))


class RefreshView(APIView):
    """Renouvelle l'access token tant que le refresh token est valide."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        auth=[],
        request=RefreshRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description="Nouvelle paire JWT ; le refresh présenté est blacklisté.",
                examples=[
                    OpenApiExample(
                        "Rotation réussie",
                        value={
                            "otp_requis": False,
                            "access_token": "<nouvel_access_token>",
                            "refresh_token": "<nouveau_refresh_token>",
                            "utilisateur": {"id": 1, "nom": "Alice Ngono"},
                        },
                        response_only=True,
                    )
                ],
            ),
            401: ErreurSerializer,
            422: ErreurSerializer,
        },
        examples=[
            OpenApiExample(
                "Refresh token",
                value={"refresh_token": "<refresh_token>"},
                request_only=True,
            )
        ],
        summary="Rafraîchir le token d'accès",
    )
    def post(self, request):
        serializer = RefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh, utilisateur = active_user_from_refresh(
            serializer.validated_data["refresh_token"]
        )
        # La rotation est activée par SIMPLE_JWT : le refresh consommé devient
        # inutilisable et une paire complète est retournée au client.
        refresh.blacklist()
        return Response(token_response(utilisateur))


class LogoutView(APIView):
    """Révoque le refresh token pour empêcher tout renouvellement ultérieur."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        request=LogoutSerializer,
        responses={204: None, 401: ErreurSerializer, 422: ErreurSerializer},
        examples=[
            OpenApiExample(
                "Révoquer le refresh token",
                value={"refresh_token": "<refresh_token>"},
                request_only=True,
            ),
            OpenApiExample(
                "Déconnexion réussie",
                value=None,
                response_only=True,
                status_codes=["204"],
            ),
        ],
        summary="Déconnexion",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh, utilisateur = active_user_from_refresh(
            serializer.validated_data["refresh_token"]
        )
        if utilisateur.id != request.user.id:
            # Un access token ne peut révoquer que les refresh tokens de son
            # propre titulaire.
            raise PermissionDenied("Ce refresh token n'appartient pas à cet utilisateur.")
        refresh.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MonProfilView(APIView):
    """Consulte et modifie le profil complet de l'utilisateur authentifié."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Utilisateurs"],
        responses={200: ProfilUtilisateurSerializer, 401: ErreurSerializer},
        summary="Récupérer mon profil",
    )
    def get(self, request):
        """Retourne les données privées accessibles à leur seul propriétaire."""
        return Response(ProfilUtilisateurSerializer(request.user).data)

    @extend_schema(
        tags=["Utilisateurs"],
        request={
            "application/json": ProfilUpdateJsonSerializer,
            "multipart/form-data": ProfilUpdateSerializer,
        },
        responses={
            200: ProfilUtilisateurSerializer,
            401: ErreurSerializer,
            422: ErreurSerializer,
        },
        summary="Modifier mon profil",
    )
    def patch(self, request):
        """Applique une mise à jour partielle et, au besoin, stocke la photo fournie."""
        serializer = ProfilUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        utilisateur = serializer.save()
        return Response(ProfilUtilisateurSerializer(utilisateur).data)


class ChangementMotDePasseView(APIView):
    """Change le mot de passe du compte après vérification de l'ancien secret."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Utilisateurs"],
        request=ChangementMotDePasseSerializer,
        responses={204: None, 401: ErreurSerializer, 422: ErreurSerializer},
        summary="Changer mon mot de passe",
    )
    def put(self, request):
        """Vérifie l'ancien mot de passe puis persiste un nouveau hash bcrypt."""
        serializer = ChangementMotDePasseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(
            serializer.validated_data["ancien_mot_de_passe"]
        ):
            # La réponse 401 est volontairement générique et ne retourne aucun
            # détail sur le hash ou la politique de mots de passe.
            raise AuthenticationFailed("Ancien mot de passe incorrect.")
        request.user.set_password(serializer.validated_data["nouveau_mot_de_passe"])
        request.user.save(update_fields=["password_hash", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfilPublicView(APIView):
    """Expose le profil public, sans donnée de contact ni privilège métier."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Utilisateurs"],
        auth=[],
        responses={200: ProfilPublicSerializer, 404: ErreurSerializer},
        summary="Récupérer le profil public d'un utilisateur",
    )
    def get(self, request, id):
        """Retourne le compte uniquement s'il possède au moins une annonce."""
        # L'existence d'une annonce, et non le rôle, définit l'éligibilité du
        # profil public. Un compte sans activité de vente reste indétectable.
        if not Annonce.objects.filter(vendeur_id=id).exists():
            raise NotFound("Utilisateur introuvable.")
        try:
            utilisateur = Utilisateur.objects.get(pk=id)
        except Utilisateur.DoesNotExist as exc:
            raise NotFound("Utilisateur introuvable.") from exc
        return Response(ProfilPublicSerializer(utilisateur).data)
