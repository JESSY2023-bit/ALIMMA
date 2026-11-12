"""Services sans état du panier conservé dans Redis."""
from decimal import Decimal, InvalidOperation

from django.core.cache import cache

from apps.catalogue.models import Annonce

from .models import ParametreSite

PANIER_TTL_SECONDES = 7 * 24 * 60 * 60
FRAIS_LIVRAISON_CLE = "frais_livraison_defaut"


def cle_panier(utilisateur_id):
    """Retourne la clé Redis stable et isolée d'un panier utilisateur."""
    return f"panier:{utilisateur_id}"


def lire_contenu(utilisateur_id):
    """Lit et normalise le contenu Redis sans jamais y stocker de prix."""
    contenu = cache.get(cle_panier(utilisateur_id), {})
    if not isinstance(contenu, dict):
        return {}
    resultat = {}
    for annonce_id, quantite in contenu.items():
        try:
            annonce_id = int(annonce_id)
            quantite = int(quantite)
        except (TypeError, ValueError):
            continue
        if annonce_id > 0 and quantite > 0:
            resultat[str(annonce_id)] = quantite
    return resultat


def enregistrer_contenu(utilisateur_id, contenu):
    """Enregistre le panier pour sept jours à compter de sa dernière activité."""
    cle = cle_panier(utilisateur_id)
    if contenu:
        cache.set(cle, contenu, timeout=PANIER_TTL_SECONDES)
    else:
        cache.delete(cle)


def frais_livraison():
    """Lit les frais configurés, ou zéro si le paramètre n'est pas encore défini."""
    valeur = ParametreSite.objects.filter(cle=FRAIS_LIVRAISON_CLE).values_list(
        "valeur", flat=True
    ).first()
    try:
        frais = Decimal(valeur) if valeur is not None else Decimal("0")
    except (InvalidOperation, TypeError):
        return Decimal("0")
    return max(frais, Decimal("0"))


def construire_panier(utilisateur_id):
    """Recalcule les lignes et retire les annonces devenues indisponibles."""
    contenu = lire_contenu(utilisateur_id)
    ids = [int(annonce_id) for annonce_id in contenu]
    annonces = (
        Annonce.objects.filter(id__in=ids, statut=Annonce.Statut.ACTIVE)
        .select_related("vendeur", "categorie")
        .prefetch_related("images")
    )
    par_id = {annonce.id: annonce for annonce in annonces}
    articles = []
    indisponibles = False
    contenu_valide = {}
    for annonce_id, quantite in contenu.items():
        annonce = par_id.get(int(annonce_id))
        if annonce is None:
            indisponibles = True
            continue
        contenu_valide[annonce_id] = quantite
        total_ligne = annonce.prix * quantite
        articles.append(
            {
                "annonce": annonce,
                "quantite": quantite,
                "prix_unitaire": annonce.prix,
                "total_ligne": total_ligne,
            }
        )
    enregistrer_contenu(utilisateur_id, contenu_valide)
    sous_total = sum((article["total_ligne"] for article in articles), Decimal("0"))
    frais = frais_livraison() if articles else Decimal("0")
    resultat = {
        "articles": articles,
        "sous_total": sous_total,
        "frais_livraison": frais,
        "total": sous_total + frais,
    }
    if indisponibles:
        resultat["message"] = "Les annonces devenues indisponibles ont été retirées du panier."
    return resultat
