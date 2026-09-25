"""Services de sécurité utilisés par les endpoints d'authentification."""
import hashlib

from django.core.cache import cache


class LoginAttemptLimiter:
    """Limite les tentatives Redis sans exposer l'identifiant en clair."""

    maximum_attempts = 5
    timeout_seconds = 15 * 60

    @classmethod
    def _key(cls, identifier):
        """Construit une clé Redis opaque et stable pour un identifiant normalisé."""
        fingerprint = hashlib.sha256(identifier.strip().lower().encode()).hexdigest()
        return f"auth:login-attempts:{fingerprint}"

    @classmethod
    def is_blocked(cls, identifier):
        """Indique si l'identifiant a dépassé le nombre d'essais autorisés."""
        return (cache.get(cls._key(identifier)) or 0) >= cls.maximum_attempts

    @classmethod
    def register_failure(cls, identifier):
        """Incrémente un échec en conservant une fenêtre glissante de quinze minutes."""
        key = cls._key(identifier)
        if cache.add(key, 1, timeout=cls.timeout_seconds):
            return 1
        return cache.incr(key)

    @classmethod
    def clear(cls, identifier):
        """Supprime les échecs après une authentification réussie."""
        cache.delete(cls._key(identifier))
