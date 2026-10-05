"""Paramètres de production."""

import os

from .base import *  # noqa: F403


def _env_list(name: str, default: tuple[str, ...] = ()) -> list[str]:
    """Retourne une variable d'environnement séparée par des virgules."""
    value = os.environ.get(name)
    if value is None:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


# La production ne doit jamais activer DEBUG, y compris par erreur dans l'env.
DEBUG = False

# Les secrets et hôtes publics sont fournis exclusivement par Render.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS")

# Le proxy HTTPS de Render transmet ce header à l'application Django.
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Aucune origine n'est implicite en production.
CORS_ALLOWED_ORIGINS = _env_list("CORS_ALLOWED_ORIGINS")

# Redis est un service externe en production : aucune URL locale par défaut.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ["REDIS_URL"],
    }
}
