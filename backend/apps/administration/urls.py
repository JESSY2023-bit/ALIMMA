"""Routes d'administration API."""
from django.urls import path

from .views import (
    RoleUtilisateurView,
    SuspensionUtilisateurView,
    UtilisateursAdministrationView,
)

urlpatterns = [
    path(
        "admin/utilisateurs",
        UtilisateursAdministrationView.as_view(),
        name="admin-utilisateurs",
    ),
    path(
        "admin/utilisateurs/<int:id>/suspendre",
        SuspensionUtilisateurView.as_view(),
        name="admin-utilisateur-suspendre",
    ),
    path(
        "admin/utilisateurs/<int:id>/role",
        RoleUtilisateurView.as_view(),
        name="admin-utilisateur-role",
    ),
]
