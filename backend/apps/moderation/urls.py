"""Routes de modération."""
from django.urls import path

from .views import AnnoncesModerationView, DecisionAnnonceModerationView

urlpatterns = [
    path("moderation/annonces", AnnoncesModerationView.as_view(), name="moderation-annonces"),
    path(
        "moderation/annonces/<int:id>/decision",
        DecisionAnnonceModerationView.as_view(),
        name="moderation-annonce-decision",
    ),
]
