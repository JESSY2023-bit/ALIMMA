"""Adaptateurs sans état vers les fournisseurs d'envoi SMS."""
import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)


class FournisseurSMS:
    """Contrat minimal que doit respecter un fournisseur SMS."""

    nom = "inconnu"

    def envoyer(self, telephone, message):
        """Envoie un message et lève une exception en cas d'échec fournisseur."""
        raise NotImplementedError


class ConsoleSMS(FournisseurSMS):
    """Fournisseur local qui journalise sans divulguer le numéro complet."""

    nom = "console"

    def envoyer(self, telephone, message):
        """Écrit un événement de développement sans secret ni donnée personnelle brute."""
        logger.info("SMS ALIMMA simulé", extra={"canal": "sms", "longueur": len(message)})


class HttpSMS(FournisseurSMS):
    """Client HTTP générique pour un agrégateur SMS configurable."""

    nom = "http"

    def envoyer(self, telephone, message):
        """Soumet le message sans jamais enregistrer la clé ou le corps de la requête."""
        if not settings.SMS_API_URL or not settings.SMS_API_KEY:
            raise RuntimeError("Le fournisseur SMS HTTP n'est pas configuré.")
        payload = json.dumps(
            {"to": telephone, "from": settings.SMS_SENDER, "message": message}
        ).encode("utf-8")
        request = Request(
            settings.SMS_API_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {settings.SMS_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                if response.status >= 300:
                    raise RuntimeError("Le fournisseur SMS a refusé la demande.")
        except (HTTPError, URLError) as exc:
            raise RuntimeError("Le fournisseur SMS est indisponible.") from exc


def fournisseur_sms():
    """Sélectionne explicitement le transport de l'environnement courant."""
    if settings.SMS_PROVIDER == "http":
        return HttpSMS()
    return ConsoleSMS()
