"""Fonctions réutilisables de validation des données de compte."""
import re


CAMEROON_PHONE_PATTERN = re.compile(r"^\+237\d{9}$")
TELEPHONE_ERROR_MESSAGE = "Le téléphone doit être au format +237XXXXXXXXX."


def normaliser_telephone(valeur):
    """Normalise un numéro camerounais local en format E.164.

    Les espaces et tirets sont tolérés afin de conserver le comportement de
    l'inscription. Un numéro national de neuf chiffres reçoit l'indicatif
    camerounais par défaut.
    """
    telephone = str(valeur or "").strip().replace(" ", "").replace("-", "")
    if telephone.isdigit() and len(telephone) == 9:
        telephone = f"+237{telephone}"
    if not CAMEROON_PHONE_PATTERN.fullmatch(telephone):
        raise ValueError(TELEPHONE_ERROR_MESSAGE)
    return telephone
