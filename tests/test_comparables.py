def test_comparables_endpoint(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/comparables",
        json=valid_property,
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["algorithm"]
        == "K-Nearest Neighbors"
    )

    assert (
        data["candidate_strategy"]
        == "same_zipcode"
    )

    assert data["count"] == 5

    assert len(data["comparables"]) == 5


def test_comparables_are_same_zipcode(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/comparables",
        json=valid_property,
    )

    comparables = (
        response
        .json()["comparables"]
    )

    target_zipcode = (
        valid_property["zipcode"]
    )

    for comparable in comparables:

        assert (
            comparable["zipcode"]
            == target_zipcode
        )


def test_comparables_have_valid_prices(
    client,
    valid_property,
):

    response = client.post(
        "/api/v1/comparables",
        json=valid_property,
    )

    comparables = (
        response
        .json()["comparables"]
    )

    for comparable in comparables:

        assert comparable["sale_price"] > 0

        assert (
            comparable["similarity_score"]
            >= 0
        )

        assert (
            comparable["similarity_score"]
            <= 100
        )