"""Tests des routes et métadonnées de documentation OpenAPI."""
import yaml
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from drf_spectacular.generators import SchemaGenerator


def test_documentation_routes_are_public(client):
    """Les trois documents sont accessibles sans jeton JWT."""
    assert client.get("/v1/schema/").status_code == 200
    assert client.get("/v1/docs/").status_code == 200
    assert client.get("/v1/redoc/").status_code == 200


def test_generated_schema_declares_jwt_and_reference_tags():
    """Le document produit conserve le mécanisme JWT et les tags ALIMMA."""
    schema = SchemaGenerator().get_schema(request=None, public=True)
    security = schema["components"]["securitySchemes"]["bearerAuth"]
    tags = {tag["name"] for tag in schema["tags"]}

    assert security == {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    assert {"Auth", "Annonces", "Administration"} <= tags


def test_comparison_command_can_fail_for_a_difference(tmp_path):
    """Le mode CI retourne une erreur lorsqu'un contrat diverge."""
    reference = tmp_path / "reference.yaml"
    reference.write_text(yaml.safe_dump({"openapi": "3.0.3"}), encoding="utf-8")

    with pytest.raises(CommandError):
        call_command("compare_openapi", "--reference", str(reference), "--fail-on-diff")
