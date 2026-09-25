"""Routes de l'authentification et des utilisateurs."""
from django.urls import path

from .views import InscriptionView, LoginView, LogoutView, RefreshView

urlpatterns = [
    path("auth/inscription", InscriptionView.as_view(), name="inscription"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", RefreshView.as_view(), name="refresh"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
]
