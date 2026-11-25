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
    # Le tuple associe explicitement chaque chemin à sa méthode publique :
    # déclarer seulement le chemin rendrait par erreur publics ses autres verbes.
    for path, methode in (
        ("/v1/auth/inscription", "post"),
        ("/v1/auth/login", "post"),
        ("/v1/auth/refresh", "post"),
        ("/v1/admin/categories", "get"),
        ("/v1/annonces", "get"),
        ("/v1/annonces/carte", "get"),
    ):
        operation = paths.get(path, {}).get(methode)
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
ALLOWED_HOSTS = [host for host in os.environ.get("ALLOWED_HOSTS", "").split(",") if host]

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
    "config.middleware.RequestIdMiddleware",
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
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "OPTIONS": {
            "sslmode": os.environ.get("POSTGRES_SSLMODE", "prefer"),
        },
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
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
# Le stockage par défaut est local en développement. Les vues utilisent
# ``default_storage`` : un stockage objet pourra être configuré sans changer
# la logique métier de l'API.
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))
MEDIA_BACKEND = os.environ.get(
    "MEDIA_BACKEND",
    "s3" if os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith(".prod") else "local",
).lower()
if MEDIA_BACKEND not in {"local", "s3"}:
    raise ValueError("MEDIA_BACKEND doit valoir local ou s3.")
AWS_QUERYSTRING_AUTH = (
    os.environ.get("AWS_QUERYSTRING_AUTH", "false").strip().lower() == "true"
)

# Le backend local reste pratique en développement et pendant les tests. En
# production, le stockage S3 compatible (Cloudflare R2 ou AWS S3) rend les
# fichiers indépendants du disque éphémère de Render.
STORAGES = {
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}
if MEDIA_BACKEND == "s3":
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.environ["AWS_STORAGE_BUCKET_NAME"],
            "endpoint_url": os.environ.get("AWS_S3_ENDPOINT_URL") or None,
            "access_key": os.environ["AWS_ACCESS_KEY_ID"],
            "secret_key": os.environ["AWS_SECRET_ACCESS_KEY"],
            "custom_domain": os.environ.get("AWS_S3_CUSTOM_DOMAIN") or None,
            # Les médias de la marketplace sont publics : une URL stable est
            # nécessaire pour les réponses API et les CDN Cloudflare.
            "querystring_auth": AWS_QUERYSTRING_AUTH,
            "file_overwrite": False,
        },
    }
# Les limites sont centralisées pour garder la validation des fichiers claire
# et configurable selon le stockage retenu.
PROFILE_PHOTO_MAX_SIZE = int(os.environ.get("PROFILE_PHOTO_MAX_SIZE", 2 * 1024 * 1024))
PROFILE_PHOTO_ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
# Les images d'annonce utilisent le même stockage interchangeable que les photos
# de profil, avec des limites adaptées à des photos de produits.
ANNONCE_IMAGE_MAX_SIZE = int(os.environ.get("ANNONCE_IMAGE_MAX_SIZE", 5 * 1024 * 1024))
ANNONCE_IMAGE_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Django s'appuie sur le modèle métier ``utilisateurs`` et non sur auth.User.
AUTH_USER_MODEL = "accounts.Utilisateur"

# Le hachage bcrypt est imposé par le contrat de sécurité ALIMMA.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.BCryptSHA256PasswordHasher"]
FEATURE_2FA_ENABLED = os.environ.get("FEATURE_2FA_ENABLED", "false").lower() == "true"

# Les chemins OpenAPI sont déjà préfixés par ``/v1``. Le serveur exposé à
# Swagger doit donc être une origine seule, sans ce suffixe, pour éviter que
# le bouton « Try it out » ne construise ``/v1/v1/...``.
API_PUBLIC_URL = os.environ.get(
    "API_PUBLIC_URL", "https://alimma.onrender.com"
).strip().rstrip("/")
if API_PUBLIC_URL.endswith("/v1"):
    # Cette normalisation protège la documentation si une ancienne valeur
    # incluant le préfixe API demeure dans l'environnement de déploiement.
    API_PUBLIC_URL = API_PUBLIC_URL[:-3]

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
    "DEFAULT_THROTTLE_CLASSES": (
        "config.throttling.ClientIPAnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "config.throttling.ClientIPScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("THROTTLE_ANON_RATE", "120/minute"),
        "user": os.environ.get("THROTTLE_USER_RATE", "1000/day"),
        "inscription": os.environ.get("THROTTLE_INSCRIPTION_RATE", "5/hour"),
        "login": os.environ.get("THROTTLE_LOGIN_RATE", "10/minute"),
        "otp": os.environ.get("THROTTLE_OTP_RATE", "3/hour"),
        "publication": os.environ.get("THROTTLE_PUBLICATION_RATE", "20/day"),
        "public": os.environ.get("THROTTLE_PUBLIC_RATE", "120/minute"),
    },
    # DRF interprète X-Forwarded-For selon cette même topologie de proxy.
    "NUM_PROXIES": int(os.environ.get("NUM_PROXIES", "0")),
}

# Un X-Forwarded-For n'est utilisé que si ce nombre de proxys est explicite.
NUM_PROXIES = int(os.environ.get("NUM_PROXIES", "0"))

# Le format JSON est lisible par Render, Sentry et les agrégateurs de logs.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "config.request_context.RequestIdFilter"}},
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["request_id"],
        }
    },
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# Sentry ne s'initialise jamais sans DSN : le poste local ne transmet aucune
# erreur à un service tiers par défaut.
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0")),
        send_default_pii=False,
        environment=os.environ.get("DJANGO_ENV", "development"),
    )

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
        {"url": API_PUBLIC_URL, "description": "Déployé, Render"},
        {"url": "http://localhost:8000", "description": "Local"},
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
