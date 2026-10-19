def test_complete_analysis_pipeline(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/analyze",
        json=valid_property,
    )

    assert response.status_code == 200

    data = response.json()

    assert "property" in data
    assert "valuation" in data

    assert (
        "valuation_explanation"
        in data
    )

    assert (
        "comparable_analysis"
        in data
    )

    assert "market_analysis" in data


def test_analysis_property_echo(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/analyze",
        json=valid_property,
    )

    property_data = (
        response
        .json()["property"]
    )

    assert property_data["zipcode"] == 98052

    assert property_data["bedrooms"] == 4

    assert property_data["bathrooms"] == 3

    assert (
        property_data["sqft_living"]
        == 3200
    )

    assert (
        property_data["year_built"]
        == 2005
    )


def test_analysis_valuation(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/analyze",
        json=valid_property,
    )

    valuation = (
        response
        .json()["valuation"]
    )

    assert (
        valuation["algorithm"]
        == "XGBoost"
    )

    assert (
        valuation["estimated_value"]
        > 0
    )


def test_analysis_comparable_median(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/analyze",
        json=valid_property,
    )

    comparable_analysis = (
        response
        .json()["comparable_analysis"]
    )

    prices = [
        comparable["sale_price"]
        for comparable
        in comparable_analysis[
            "comparables"
        ]
    ]

    sorted_prices = sorted(prices)

    expected_median = (
        sorted_prices[
            len(sorted_prices) // 2
        ]
    )

    assert (
        comparable_analysis[
            "median_comparable_price"
        ]
        == expected_median
    )


def test_analysis_algorithms(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/analyze",
        json=valid_property,
    )

    data = response.json()

    assert (
        data["valuation"]["algorithm"]
        == "XGBoost"
    )

    assert (
        data[
            "comparable_analysis"
        ]["algorithm"]
        == "K-Nearest Neighbors"
    )

    assert (
        data[
            "market_analysis"
        ]["algorithm"]
        == "K-Means"
    )