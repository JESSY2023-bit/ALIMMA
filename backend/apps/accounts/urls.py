"""Routes de l'authentification et des utilisateurs."""
from django.urls import path

from .views import (
    ChangementMotDePasseView,
    InscriptionView,
    LoginView,
    LogoutView,
    MonProfilView,
    ProfilPublicView,
    RefreshView,
    VerifyOtpView,
    RenvoyerOtpView,
    MotDePasseOublieView,
    VerifierMotDePasseOublieView,
    ReinitialiserMotDePasseView,
)

urlpatterns = [
    path("auth/inscription", InscriptionView.as_view(), name="inscription"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", RefreshView.as_view(), name="refresh"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("auth/verify-otp", VerifyOtpView.as_view(), name="verify-otp"),
    path("auth/renvoyer-otp", RenvoyerOtpView.as_view(), name="renvoyer-otp"),
    path(
        "auth/mot-de-passe-oublie",
        MotDePasseOublieView.as_view(),
        name="mot-de-passe-oublie",
    ),
    path(
        "auth/mot-de-passe-oublie/verifier",
        VerifierMotDePasseOublieView.as_view(),
        name="mot-de-passe-oublie-verifier",
    ),
    path(
        "auth/mot-de-passe-oublie/reinitialiser",
        ReinitialiserMotDePasseView.as_view(),
        name="mot-de-passe-oublie-reinitialiser",
    ),
    path("utilisateurs/moi", MonProfilView.as_view(), name="mon-profil"),
    path(
        "utilisateurs/moi/mot-de-passe",
        ChangementMotDePasseView.as_view(),
        name="changement-mot-de-passe",
    ),
    path("utilisateurs/<int:id>", ProfilPublicView.as_view(), name="profil-public"),
]
