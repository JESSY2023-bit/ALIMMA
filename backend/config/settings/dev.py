"""Paramètres locaux de développement."""
from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
CORS_ALLOWED_ORIGINS = [
    origin for origin in __import__("os").environ.get(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",") if origin
]
