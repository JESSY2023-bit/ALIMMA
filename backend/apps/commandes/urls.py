"""Routes du panier et des futures commandes."""
from django.urls import path

from .views import (
    CommandeActionView,
    CommandeDetailView,
    CommandesView,
    PanierArticleDetailView,
    PanierArticlesView,
    PanierView,
)

urlpatterns = [
    path("panier", PanierView.as_view(), name="panier"),
    path("commandes", CommandesView.as_view(), name="commandes"),
    path("commandes/<int:id>", CommandeDetailView.as_view(), name="commande-detail"),
    path(
        "commandes/<int:id>/accepter",
        CommandeActionView.as_view(),
        {"action": "accepter"},
        name="commande-accepter",
    ),
    path(
        "commandes/<int:id>/refuser",
        CommandeActionView.as_view(),
        {"action": "refuser"},
        name="commande-refuser",
    ),
    path(
        "commandes/<int:id>/annuler",
        CommandeActionView.as_view(),
        {"action": "annuler"},
        name="commande-annuler",
    ),
    path(
        "commandes/<int:id>/expedier",
        CommandeActionView.as_view(),
        {"action": "expedier"},
        name="commande-expedier",
    ),
    path(
        "commandes/<int:id>/confirmer-reception",
        CommandeActionView.as_view(),
        {"action": "confirmer-reception"},
        name="commande-confirmer-reception",
    ),
    path("panier/articles", PanierArticlesView.as_view(), name="panier-articles"),
    path(
        "panier/articles/<int:annonce_id>",
        PanierArticleDetailView.as_view(),
        name="panier-article-detail",
    ),
]
