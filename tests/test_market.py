def test_market_analysis(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/analyze",
        json=valid_property,
    )

    assert response.status_code == 200

    market = (
        response
        .json()["market_analysis"]
    )

    assert market["available"] is True

    assert market["zipcode"] == 98052

    assert (
        market["segment"]
        == "High-Value Market"
    )

    assert market["cluster"] == 1

    assert (
        market["algorithm"]
        == "K-Means"
    )


def test_market_reference_statistics(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/analyze",
        json=valid_property,
    )

    market = (
        response
        .json()["market_analysis"]
    )

    assert market["property_count"] == 574

    assert market["median_price"] > 0

    assert (
        market["median_price_per_sqft"]
        > 0
    )

    assert (
        market["silhouette_score"]
        > 0
    )