def test_root_endpoint(client):

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "EstateIQ"
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"


def test_health_endpoint(client):

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert (
        data["services"]["api"]
        == "available"
    )

    assert (
        data["services"]["valuation_model"]
        == "available"
    )