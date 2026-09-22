"""Paramètres de production."""
from .base import *  # noqa: F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CORS_ALLOWED_ORIGINS = [
    origin for origin in __import__("os").environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if origin
]
