"""Services de sécurité utilisés par les endpoints d'authentification."""
import hashlib
import secrets

from django.core.cache import cache

from config.network import ip_client
from apps.notifications.services import notifier


class OtpService:
    """Gère des codes OTP opaques, hachés et limités dans Redis."""

    INSCRIPTION = "inscription"
    REINITIALISATION = "reinitialisation"
    DUREES = {INSCRIPTION: 5 * 60, REINITIALISATION: 15 * 60}
    MAX_ESSAIS = 3

    @classmethod
    def _empreinte(cls, valeur):
        """Produit une clé Redis qui ne révèle jamais un téléphone ou un jeton."""
        return hashlib.sha256(valeur.encode()).hexdigest()

    @classmethod
    def _cle(cls, telephone, objectif):
        return f"auth:otp:{objectif}:{cls._empreinte(telephone)}"

    @classmethod
    def envoyer(cls, utilisateur, objectif):
        """Génère un code à six chiffres et mémorise uniquement son empreinte."""
        code = f"{secrets.randbelow(1_000_000):06d}"
        cache.set(
            cls._cle(utilisateur.telephone, objectif),
            {"hash": cls._empreinte(code), "essais": 0},
            timeout=cls.DUREES[objectif],
        )
        notifier(
            utilisateur,
            "otp",
            {"code": code, "duree_minutes": cls.DUREES[objectif] // 60},
            canaux=("sms",),
        )

    @classmethod
    def verifier(cls, telephone, code, objectif):
        """Valide une seule fois un OTP et bloque dès le quatrième essai."""
        cle = cls._cle(telephone, objectif)
        donnees = cache.get(cle)
        if not donnees or donnees["essais"] >= cls.MAX_ESSAIS:
            return False
        if not secrets.compare_digest(donnees["hash"], cls._empreinte(code)):
            donnees["essais"] += 1
            # Le timeout initial est conservé : un bruteforce ne prolonge pas la vie du code.
            cache.set(cle, donnees, timeout=cls.DUREES[objectif])
            return False
        cache.delete(cle)
        return True

    @classmethod
    def creer_jeton_reinitialisation(cls, utilisateur):
        """Crée un jeton opaque, à usage unique, valable dix minutes."""
        jeton = secrets.token_urlsafe(32)
        cache.set(f"auth:reset:{cls._empreinte(jeton)}", utilisateur.id, timeout=10 * 60)
        return jeton

    @classmethod
    def consommer_jeton_reinitialisation(cls, jeton):
        """Retourne l'identifiant puis retire immédiatement le jeton Redis."""
        cle = f"auth:reset:{cls._empreinte(jeton)}"
        utilisateur_id = cache.get(cle)
        cache.delete(cle)
        return utilisateur_id


class LoginAttemptLimiter:
    """Limite les tentatives Redis sans exposer l'identifiant en clair."""

    maximum_attempts = 5
    timeout_seconds = 15 * 60

    @classmethod
    def _key(cls, identifier, request):
        """Construit une clé Redis opaque et stable pour un identifiant normalisé."""
        valeur = f"{identifier.strip().lower()}:{ip_client(request)}"
        fingerprint = hashlib.sha256(valeur.encode()).hexdigest()
        return f"auth:login-attempts:{fingerprint}"

    @classmethod
    def is_blocked(cls, identifier, request):
        """Indique si l'identifiant a dépassé le nombre d'essais autorisés."""
        return (cache.get(cls._key(identifier, request)) or 0) >= cls.maximum_attempts

    @classmethod
    def register_failure(cls, identifier, request):
        """Incrémente un échec en conservant une fenêtre glissante de quinze minutes."""
        key = cls._key(identifier, request)
        # ``add`` initialise l'expiration une seule fois ; les incréments
        # suivants ne prolongent donc pas indéfiniment le blocage.
        if cache.add(key, 1, timeout=cls.timeout_seconds):
            return 1
        return cache.incr(key)

    @classmethod
    def clear(cls, identifier, request):
        """Supprime les échecs après une authentification réussie."""
        cache.delete(cls._key(identifier, request))
