"""Routes du catalogue."""
from django.urls import path

from .views import (
    AnnonceDetailView,
    AnnoncesCarteView,
    AnnoncesView,
    CategoriesAdministrationView,
    CategorieAdministrationDetailView,
    MesAnnoncesView,
    PauseAnnonceView,
)

urlpatterns = [
    path("annonces", AnnoncesView.as_view(), name="annonces"),
    path("annonces/carte", AnnoncesCarteView.as_view(), name="annonces-carte"),
    path("annonces/<int:id>", AnnonceDetailView.as_view(), name="annonce-detail"),
    path("annonces/<int:id>/pause", PauseAnnonceView.as_view(), name="annonce-pause"),
    path("utilisateurs/moi/annonces", MesAnnoncesView.as_view(), name="mes-annonces"),
    path("admin/categories", CategoriesAdministrationView.as_view(), name="admin-categories"),
    path(
        "admin/categories/<int:id>",
        CategorieAdministrationDetailView.as_view(),
        name="admin-categorie-detail",
    ),
]
