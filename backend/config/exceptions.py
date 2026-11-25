"""Format d'erreur public défini par le contrat OpenAPI."""
from rest_framework.exceptions import AuthenticationFailed, Throttled
from rest_framework.views import exception_handler as drf_exception_handler


def _first_message(detail):
    """Extrait un message lisible depuis les détails parfois imbriqués de DRF."""
    if isinstance(detail, dict):
        return _first_message(next(iter(detail.values()), "Erreur de validation."))
    if isinstance(detail, (list, tuple)):
        return _first_message(detail[0]) if detail else "Erreur de validation."
    return str(detail)


def _messages_de_validation(detail):
    """Transforme les erreurs DRF d'un champ en liste de messages sérialisables."""
    if isinstance(detail, dict):
        # Une erreur imbriquée ne peut pas être représentée directement dans
        # le contrat ``{champ: [messages]}``. Le premier message reste utile
        # au frontend tout en conservant le nom du champ de niveau supérieur.
        return [_first_message(detail)]
    if isinstance(detail, (list, tuple)):
        return [str(message) for message in detail]
    return [str(detail)]


def _details_de_validation(detail):
    """Construit ``{nom_du_champ: [messages]}`` à partir du détail DRF."""
    if isinstance(detail, dict):
        return {
            str(champ): _messages_de_validation(messages)
            for champ, messages in detail.items()
        }
    # Les erreurs sans champ explicite restent exploitables par le client.
    return {"non_field_errors": _messages_de_validation(detail)}


def api_exception_handler(exc, context):
    """Convertit les exceptions DRF en ``{code, message}``."""
    # Le gestionnaire DRF conserve le traitement standard des exceptions qu'il
    # connaît, puis ce projet normalise uniquement la réponse publique.
    response = drf_exception_handler(exc, context)
    if response is None:
        return response

    # DRF transforme AuthenticationFailed en 403 lorsque la vue est publique.
    # Le contrat ALIMMA impose néanmoins 401 pour des identifiants ou tokens invalides.
    if isinstance(exc, AuthenticationFailed):
        response.status_code = 401
    if isinstance(exc, Throttled):
        response.data = {
            "code": "RATE_LIMITED",
            "message": "Trop de requêtes. Veuillez réessayer plus tard.",
        }
        return response
    # DRF peut retourner un dictionnaire (erreur de champ) ou une liste
    # (ValidationError construite depuis une simple chaîne). Les deux formes
    # doivent être normalisées sans provoquer une erreur 500.
    detail = (
        response.data.get("detail", response.data)
        if isinstance(response.data, dict)
        else response.data
    )
    if response.status_code == 400:
        # Le contrat ALIMMA expose les erreurs de validation en 422.
        response.status_code = 422
        response.data = {
            "code": "VALIDATION_ERROR",
            # Le message historique est conservé pour les clients existants ;
            # ``details`` apporte le nom précis du champ au nouveau frontend.
            "message": _first_message(detail),
            "details": _details_de_validation(detail),
        }
        return response
    default_code = "VALIDATION_ERROR" if response.status_code == 422 else "API_ERROR"
    code = default_code if response.status_code == 422 else getattr(
        exc, "default_code", default_code
    ).upper()
    response.data = {"code": code, "message": _first_message(detail)}
    return response
