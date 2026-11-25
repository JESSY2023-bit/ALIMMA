"""Middlewares transverses de l'API ALIMMA."""
import logging
import uuid

from .request_context import request_id_context


logger = logging.getLogger("django.request")


class RequestIdMiddleware:
    """Propage un identifiant de requête fiable dans les logs et la réponse."""

    header_name = "HTTP_X_REQUEST_ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Conserve un identifiant entrant sain ou en génère un nouveau."""
        incoming = request.META.get(self.header_name, "").strip()
        request_id = incoming if incoming and len(incoming) <= 128 else str(uuid.uuid4())
        token = request_id_context.set(request_id)
        request.request_id = request_id
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            logger.info(
                "Requête traitée",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                },
            )
            return response
        finally:
            request_id_context.reset(token)
