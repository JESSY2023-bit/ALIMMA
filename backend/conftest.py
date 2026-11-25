"""Fixtures communes garantissant l'isolation des états Redis entre tests."""
import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def vider_cache_entre_tests():
    """Évite qu'un quota ou une vue mémorisée influence un autre scénario.

    Les limites DRF vivent volontairement dans Redis en production. Sans cette
    isolation, les clients Django de plusieurs tests partagent ``testserver``
    et peuvent consommer le même quota de connexion.
    """
    cache.clear()
    yield
    cache.clear()
