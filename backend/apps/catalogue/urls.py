"""Routes du catalogue."""
from django.urls import path

from .views import CategoriesAdministrationView, CategorieAdministrationDetailView

urlpatterns = [
    path("admin/categories", CategoriesAdministrationView.as_view(), name="admin-categories"),
    path(
        "admin/categories/<int:id>",
        CategorieAdministrationDetailView.as_view(),
        name="admin-categorie-detail",
    ),
]
