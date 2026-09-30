"""Paramètres de production."""
from .base import *  # noqa: F403

DEBUG = False
# Le proxy HTTPS doit transmettre ``X-Forwarded-Proto`` pour éviter les
# redirections erronées et garantir des cookies réservés au canal TLS.
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Aucune origine CORS n'est implicite en production : elles sont déclarées par
# l'environnement de déploiement.
CORS_ALLOWED_ORIGINS = [
    origin for origin in __import__("os").environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if origin
]
