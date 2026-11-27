"""Gabarits courts, relus et localisés des notifications transactionnelles."""

GABARITS = {
    "annonce_validee": {
        "fr": "ALIMMA : votre annonce « {titre} » est validée.",
        "en": "ALIMMA: your listing “{titre}” was approved.",
    },
    "annonce_rejetee": {
        "fr": "ALIMMA : votre annonce « {titre} » est rejetée. Motif : {motif}",
        "en": "ALIMMA: your listing “{titre}” was rejected. Reason: {motif}",
    },
    "role_modifie": {
        "fr": "ALIMMA : votre rôle est maintenant « {role} ».",
        "en": "ALIMMA: your role is now “{role}”.",
    },
    "commande_statut": {
        "fr": "ALIMMA : la commande #{commande_id} est {statut}.",
        "en": "ALIMMA: order #{commande_id} is now {statut}.",
    },
    "otp": {
        "fr": "ALIMMA : votre code de vérification est {code}. Valable {duree_minutes} min.",
        "en": "ALIMMA: your verification code is {code}. Valid for {duree_minutes} min.",
    },
}


def rendre_gabarit(gabarit, contexte, langue="fr"):
    """Retourne le texte localisé en limitant strictement un SMS à 160 caractères."""
    try:
        texte = GABARITS[gabarit].get(langue, GABARITS[gabarit]["fr"])
    except KeyError as exc:
        raise ValueError("Gabarit de notification inconnu.") from exc
    return texte.format(**contexte)[:160]
