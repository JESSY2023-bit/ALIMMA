"""Routes du panier et des futures commandes."""
from django.urls import path

from .views import CommandesView, PanierArticleDetailView, PanierArticlesView, PanierView

urlpatterns = [
    path("panier", PanierView.as_view(), name="panier"),
    path("commandes", CommandesView.as_view(), name="commandes"),
    path("panier/articles", PanierArticlesView.as_view(), name="panier-articles"),
    path(
        "panier/articles/<int:annonce_id>",
        PanierArticleDetailView.as_view(),
        name="panier-article-detail",
    ),
]
