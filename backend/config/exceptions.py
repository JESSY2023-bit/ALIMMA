"""Format d'erreur public défini par le contrat OpenAPI."""
from rest_framework.views import exception_handler as drf_exception_handler


def _first_message(detail):
    """Extrait un message lisible depuis les détails parfois imbriqués de DRF."""
    if isinstance(detail, dict):
        return _first_message(next(iter(detail.values()), "Erreur de validation."))
    if isinstance(detail, (list, tuple)):
        return _first_message(detail[0]) if detail else "Erreur de validation."
    return str(detail)


def api_exception_handler(exc, context):
    """Convertit les exceptions DRF en ``{code, message}``."""
    response = drf_exception_handler(exc, context)
    if response is None:
        return response

    detail = response.data.get("detail", response.data)
    if response.status_code == 400:
        # Le contrat ALIMMA expose les erreurs de validation en 422.
        response.status_code = 422
    default_code = "VALIDATION_ERROR" if response.status_code == 422 else "API_ERROR"
    code = default_code if response.status_code == 422 else getattr(
        exc, "default_code", default_code
    ).upper()
    response.data = {"code": code, "message": _first_message(detail)}
    return response
