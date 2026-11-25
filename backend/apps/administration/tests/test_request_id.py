"""Tests du corrélateur transmis dans chaque réponse HTTP."""


def test_request_id_entrant_est_repris_dans_la_reponse(client):
    """Le frontend peut corréler une erreur API à un journal structuré."""
    response = client.get("/v1/schema/", HTTP_X_REQUEST_ID="trace-front-123")

    assert response.status_code == 200
    assert response["X-Request-ID"] == "trace-front-123"


def test_request_id_est_genere_lorsqu_il_est_absent(client):
    """Chaque réponse possède un identifiant même sans en-tête client."""
    response = client.get("/v1/schema/")

    assert response.status_code == 200
    assert response["X-Request-ID"]
