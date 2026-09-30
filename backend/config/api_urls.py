"""Agrégation des routes versionnées de l'API."""
from django.urls import include, path

urlpatterns = [
    # Chaque domaine gère ses propres routes, toutes sous le préfixe /v1/.
    path("", include("apps.accounts.urls")),
    path("", include("apps.catalogue.urls")),
    path("", include("apps.commandes.urls")),
    path("", include("apps.moderation.urls")),
    path("", include("apps.administration.urls")),
]
