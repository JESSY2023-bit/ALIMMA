"""Routes du catalogue."""
from django.urls import path

from .views import (
    AnnoncesView,
    CategoriesAdministrationView,
    CategorieAdministrationDetailView,
)

urlpatterns = [
    path("annonces", AnnoncesView.as_view(), name="annonces"),
    path("admin/categories", CategoriesAdministrationView.as_view(), name="admin-categories"),
    path(
        "admin/categories/<int:id>",
        CategorieAdministrationDetailView.as_view(),
        name="admin-categorie-detail",
    ),
]
