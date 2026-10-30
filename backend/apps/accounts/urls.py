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
)

urlpatterns = [
    path("auth/inscription", InscriptionView.as_view(), name="inscription"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", RefreshView.as_view(), name="refresh"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("utilisateurs/moi", MonProfilView.as_view(), name="mon-profil"),
    path(
        "utilisateurs/moi/mot-de-passe",
        ChangementMotDePasseView.as_view(),
        name="changement-mot-de-passe",
    ),
    path("utilisateurs/<int:id>", ProfilPublicView.as_view(), name="profil-public"),
]
