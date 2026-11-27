"""Règles de calcul monétaire communes à la plateforme ALIMMA."""
from decimal import Decimal, ROUND_DOWN


def fcfa(valeur):
    """Retourne un montant FCFA entier, toujours arrondi à l'unité inférieure.

    Le FCFA ne possède pas de centime. La conversion par ``str`` évite les
    imprécisions d'un éventuel flottant fourni par une intégration externe.
    """
    return int(Decimal(str(valeur)).quantize(Decimal("1"), rounding=ROUND_DOWN))
