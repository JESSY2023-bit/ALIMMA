"""Classes DRF de limitation exploitant l'adresse client validée."""
import hashlib

from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle

from .network import ip_client


class ClientIPAnonRateThrottle(AnonRateThrottle):
    """Applique le quota anonyme à l'IP réelle lorsque le proxy est déclaré."""

    def get_cache_key(self, request, view):
        """Construit une clé anonyme stable à partir de l'adresse cliente."""
        if request.user and request.user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": ip_client(request)}


class ClientIPScopedRateThrottle(ScopedRateThrottle):
    """Applique les scopes publics à l'IP et les scopes privés à l'utilisateur."""

    def get_cache_key(self, request, view):
        """Construit la clé à partir du scope de la vue et de son appelant."""
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = ip_client(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class OtpTelephoneRateThrottle(ClientIPScopedRateThrottle):
    """Quota OTP prévu pour A7, partitionné par numéro plutôt que par IP."""

    scope = "otp"

    def get_cache_key(self, request, view):
        """Utilise le téléphone fourni, sans le placer en clair dans Redis."""
        telephone = request.data.get("telephone", "") if hasattr(request, "data") else ""
        if not telephone:
            return super().get_cache_key(request, view)
        ident = hashlib.sha256(telephone.strip().encode()).hexdigest()
        return self.cache_format % {"scope": self.scope, "ident": ident}
