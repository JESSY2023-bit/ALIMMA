"""Routes de l'authentification et des utilisateurs."""
from django.urls import path

from .views import InscriptionView

urlpatterns = [path("auth/inscription", InscriptionView.as_view(), name="inscription")]
