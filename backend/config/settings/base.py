"""Paramètres communs à tous les environnements."""
from datetime import timedelta
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]


def declarer_operations_publiques(result, generator, request, public):
    """Force ``security: []`` pour les opérations publiques du contrat.

    drf-spectacular omet normalement ce champ lorsque ``auth=[]``. Or le
    contrat ALIMMA le rend explicite pour que les clients sachent qu'aucun
    Bearer token n'est requis, même en présence de la sécurité globale.
    """
    paths = result.get("paths", {})
    for path in ("/v1/auth/inscription", "/v1/auth/login", "/v1/auth/refresh"):
        operation = paths.get(path, {}).get("post")
        if operation is not None:
            operation["security"] = []
    return result


# Les variables exportées par le système restent prioritaires. Le fichier local
# simplifie le développement sans être jamais versionné.
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

# Cette valeur de repli ne convient qu'au poste local : la production doit
# toujours fournir ``DJANGO_SECRET_KEY`` via son gestionnaire de secrets.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
DEBUG = False
ALLOWED_HOSTS = [host for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host]

# Les applications tierces précèdent les domaines métier afin de rendre les
# dépendances techniques et fonctionnelles immédiatement identifiables.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "apps.accounts",
    "apps.catalogue",
    "apps.commandes",
    "apps.moderation",
    "apps.administration",
]

# CORS doit rester avant CommonMiddleware pour traiter les requêtes du client
# React, y compris lorsqu'elles sont prévolées par le navigateur.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# La connexion est entièrement configurable pour ne jamais inscrire un secret
# d'infrastructure dans le dépôt.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "alimma"),
        "USER": os.environ.get("POSTGRES_USER", "alimma"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "alimma"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Django s'appuie sur le modèle métier ``utilisateurs`` et non sur auth.User.
AUTH_USER_MODEL = "accounts.Utilisateur"

# Le hachage bcrypt est imposé par le contrat de sécurité ALIMMA.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.BCryptSHA256PasswordHasher"]
FEATURE_2FA_ENABLED = os.environ.get("FEATURE_2FA_ENABLED", "false").lower() == "true"

# L'API est protégée par JWT par défaut ; les vues publiques déclarent
# explicitement ``AllowAny`` afin que leur exposition soit visible au code.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "config.exceptions.api_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Les durées sont centralisées ici pour rester cohérentes avec le contrat API.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # Chaque renouvellement rend le refresh présenté inutilisable afin de
    # limiter l'impact d'un jeton volé.
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# La documentation générée reprend les métadonnées et les tags du contrat
# OpenAPI de référence situé dans ``docs/openapi.yaml``.
SPECTACULAR_SETTINGS = {
    "TITLE": "ALIMMA API",
    "DESCRIPTION": (
        "API REST de la marketplace électronique ALIMMA (Cameroun).\n"
        "Couvre l'authentification, le catalogue d'annonces, les commandes, "
        "les paiements (Mobile Money / COD), la livraison, la modération "
        "et l'administration.\n\n"
        "## Authentification\n\n"
        "Flux : inscription → login → access + refresh → appels avec "
        "`Authorization: Bearer <access>` → expiration → refresh → logout. "
        "L'access token expire après 30 minutes et le refresh token après 7 jours. "
        "Chaque refresh retourne une nouvelle paire et blackliste le refresh "
        "précédent. Le logout blackliste le refresh fourni et empêche tout "
        "renouvellement ultérieur."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": [],
    "SERVERS": [
        {"url": "https://api.alimma.cm/v1", "description": "Production"},
        {"url": "https://staging-api.alimma.cm/v1", "description": "Staging"},
    ],
    "TAGS": [
        {"name": "Auth"},
        {"name": "Utilisateurs"},
        {"name": "Annonces"},
        {"name": "Enchères"},
        {"name": "Recherche"},
        {"name": "Panier & Commandes"},
        {"name": "Paiements"},
        {"name": "Livraison"},
        {"name": "Avis & Réputation"},
        {"name": "Social"},
        {"name": "Vendeur Pro"},
        {"name": "Modération"},
        {"name": "Administration"},
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": (
                    "Obtenez l'access token via `/auth/login`, puis envoyez-le "
                    "dans `Authorization: Bearer <access_token>`. Dans Swagger UI, "
                    "le bouton **Authorize** attend uniquement l'access token, sans "
                    "le préfixe `Bearer`."
                ),
            }
        }
    },
    "SECURITY": [{"bearerAuth": []}],
    # La sécurité globale ``bearerAuth`` est le seul mécanisme exposé au
    # contrat : les opérations publiques sont ensuite exemptées par le hook.
    "AUTHENTICATION_WHITELIST": [],
    "POSTPROCESSING_HOOKS": [
        "config.settings.base.declarer_operations_publiques",
    ],
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
}

# Redis est notamment utilisé pour limiter les tentatives de connexion.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}
