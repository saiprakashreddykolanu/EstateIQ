def test_valuation_endpoint(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/valuation",
        json=valid_property,
    )

    assert response.status_code == 200

    data = response.json()

    assert "estimated_value" in data

    assert data["currency"] == "USD"

    assert data["model"] == "XGBoost"

    assert data["model_version"] == "1.0"

    assert (
        data["market_reference"]
        == (
            "King County historical "
            "2014-2015 market"
        )
    )


def test_valuation_is_positive(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/valuation",
        json=valid_property,
    )

    value = (
        response
        .json()["estimated_value"]
    )

    assert value > 0


def test_reference_property_valuation_range(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/valuation",
        json=valid_property,
    )

    value = (
        response
        .json()["estimated_value"]
    )

    # Expected model output is around $748K.
    #
    # We intentionally use a reasonable range
    # instead of exact floating-point equality.

    assert 700000 < value < 800000