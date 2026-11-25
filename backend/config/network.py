"""Utilitaires réseau sûrs derrière un proxy inverse de confiance."""
from django.conf import settings


def ip_client(request):
    """Retourne l'adresse IP du client sans faire confiance aveuglément à XFF.

    ``X-Forwarded-For`` est une donnée contrôlable par le client lorsqu'une
    application est directement exposée. Il n'est donc interprété que si le
    déploiement déclare explicitement le nombre de proxys de confiance. Avec
    un proxy, le client se situe juste avant les adresses de ces proxys.
    """
    remote_addr = request.META.get("REMOTE_ADDR", "")
    try:
        nombre_proxys = max(int(getattr(settings, "NUM_PROXIES", 0)), 0)
    except (TypeError, ValueError):
        nombre_proxys = 0

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    chain = [adresse.strip() for adresse in forwarded_for.split(",") if adresse.strip()]
    if nombre_proxys and chain:
        # Certains reverse proxies ajoutent leur adresse dans la chaîne,
        # d'autres transmettent seulement le client. Les deux formats restent
        # sûrs ici car le réglage n'est activé que derrière un proxy fiable.
        if len(chain) > nombre_proxys:
            return chain[-(nombre_proxys + 1)]
        return chain[0]
    return remote_addr
