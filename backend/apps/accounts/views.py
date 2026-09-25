"""Vues d'authentification des utilisateurs ALIMMA."""
from django.conf import settings
from django.core import signing
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ErreurSerializer,
    InscriptionSerializer,
    LoginSerializer,
    LogoutSerializer,
    RefreshRequestSerializer,
    LoginResponseSerializer,
    UtilisateurSerializer,
)
from .models import Utilisateur
from .services import LoginAttemptLimiter

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
    refresh = refresh_token or RefreshToken.for_user(utilisateur)
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
            200: LoginResponseSerializer,
            401: ErreurSerializer,
            422: ErreurSerializer,
        },
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
            LoginAttemptLimiter.register_failure(identifier)
            raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

        LoginAttemptLimiter.clear(identifier)
        utilisateur.derniere_connexion = timezone.now()
        utilisateur.save(update_fields=["derniere_connexion", "updated_at"])
        if settings.FEATURE_2FA_ENABLED and utilisateur.deux_fa_active:
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
            200: LoginResponseSerializer,
            401: ErreurSerializer,
            422: ErreurSerializer,
        },
        summary="Rafraîchir le token d'accès",
    )
    def post(self, request):
        serializer = RefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh, utilisateur = active_user_from_refresh(
            serializer.validated_data["refresh_token"]
        )
        return Response(token_response(utilisateur, refresh))


class LogoutView(APIView):
    """Révoque le refresh token pour empêcher tout renouvellement ultérieur."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        request=LogoutSerializer,
        responses={204: None, 401: ErreurSerializer, 422: ErreurSerializer},
        summary="Déconnexion",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh, utilisateur = active_user_from_refresh(
            serializer.validated_data["refresh_token"]
        )
        if utilisateur.id != request.user.id:
            raise PermissionDenied("Ce refresh token n'appartient pas à cet utilisateur.")
        refresh.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)
