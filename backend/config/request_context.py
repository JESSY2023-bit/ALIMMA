"""Contexte de requête partagé entre le middleware et le journal applicatif."""
import contextvars
import logging


request_id_context = contextvars.ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Ajoute le corrélateur de requête à tous les enregistrements JSON."""

    def filter(self, record):
        """Garantit la présence de ``request_id`` pour chaque journalisation."""
        record.request_id = request_id_context.get()
        return True
