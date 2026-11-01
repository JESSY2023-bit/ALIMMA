"""Routes racines du projet."""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Interface Django réservée aux administrateurs de la plateforme.
    path("admin/", admin.site.urls),
    # Les trois routes exposent respectivement le contrat brut, Swagger et ReDoc.
    path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("v1/", include("config.api_urls")),
]

# En développement, Django sert les photos enregistrées localement. En
# production, cette responsabilité revient au serveur web ou au stockage objet.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
