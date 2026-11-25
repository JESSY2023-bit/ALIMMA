"""Tests de résolution d'IP réelle et de déduplication des consultations."""
import pytest
from django.core.cache import cache
from django.test import RequestFactory, override_settings

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, Categorie
from config.network import ip_client


def test_ip_client_ignore_x_forwarded_for_sans_proxy_declare():
    """Une application directement exposée ignore l'en-tête XFF forgeable."""
    request = RequestFactory().get(
        "/v1/annonces",
        HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.10",
        REMOTE_ADDR="198.51.100.10",
    )

    with override_settings(NUM_PROXIES=0):
        assert ip_client(request) == "198.51.100.10"


def test_ip_client_extrait_le_client_derriere_un_proxy_declare():
    """Le client précède l'unique proxy de confiance dans la chaîne XFF."""
    request = RequestFactory().get(
        "/v1/annonces",
        HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.10",
        REMOTE_ADDR="10.0.0.10",
    )

    with override_settings(NUM_PROXIES=1):
        assert ip_client(request) == "203.0.113.10"


def test_ip_client_accepte_la_forme_xff_client_seul_du_proxy():
    """Certains proxies fiables transmettent uniquement l'adresse du client."""
    request = RequestFactory().get(
        "/v1/annonces",
        HTTP_X_FORWARDED_FOR="203.0.113.10",
        REMOTE_ADDR="10.0.0.10",
    )

    with override_settings(NUM_PROXIES=1):
        assert ip_client(request) == "203.0.113.10"


@pytest.mark.django_db
def test_deux_clients_derriere_proxy_comptent_deux_vues(client):
    """Deux XFF distincts ne sont pas confondus avec l'IP du proxy Render."""
    cache.clear()
    vendeur = Utilisateur.objects.create_user(
        nom="Vendeur proxy",
        telephone="+237670009901",
        password="mot-de-passe-solide",
    )
    categorie = Categorie.objects.create(nom="Proxy", slug="proxy")
    annonce = Annonce.objects.create(
        vendeur=vendeur,
        categorie=categorie,
        titre="Annonce proxy",
        description="Description.",
        prix="1000.00",
        ville="Douala",
        statut=Annonce.Statut.ACTIVE,
    )

    with override_settings(NUM_PROXIES=1):
        client.get(
            f"/v1/annonces/{annonce.id}",
            HTTP_X_FORWARDED_FOR="203.0.113.10, 10.0.0.10",
            REMOTE_ADDR="10.0.0.10",
        )
        client.get(
            f"/v1/annonces/{annonce.id}",
            HTTP_X_FORWARDED_FOR="203.0.113.11, 10.0.0.10",
            REMOTE_ADDR="10.0.0.10",
        )

    annonce.refresh_from_db()
    assert annonce.nb_vues == 2
